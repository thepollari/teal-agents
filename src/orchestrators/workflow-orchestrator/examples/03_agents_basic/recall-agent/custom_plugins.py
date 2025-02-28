import os
from typing import List
from uuid import uuid4

from dotenv import load_dotenv
from openai import AzureOpenAI
from qdrant_client import models, QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse

from semantic_kernel.functions.kernel_function_decorator import kernel_function

from sk_agents.ska_types import BasePlugin

from custom_types import Memory
from sk_agents.extra_data_collector import ExtraDataCollector

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "memories"
API_KEY = os.environ["TA_API_KEY"]
AZURE_ENDPOINT = os.environ["TA_BASE_URL"]
AZURE_DEPLOYMENT = EMBEDDING_MODEL
API_VERSION = "2024-10-21"
QDRANT_HOST = os.environ.get("TA_QDRANT_HOST", "localhost")
QDRANT_PORT = 6333
VECTOR_SIZE = 1536
SCORE_THRESHOLD = 0.4
RECALL_LIMIT = 5


class MemoryPlugin(BasePlugin):
    def __init__(self, authorization: str | None = None, extra_data_collector: ExtraDataCollector | None = None):
        super().__init__(authorization, extra_data_collector)
        self.client = AzureOpenAI(
            api_key=API_KEY,
            azure_endpoint=AZURE_ENDPOINT,
            azure_deployment=AZURE_DEPLOYMENT,
            api_version=API_VERSION,
        )
        self.qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        self._check_create_memory_collection()

    @kernel_function(description="Create a new memory")
    def memory_create(self, user_id: str, content: str) -> None:
        new_memory = Memory(
            memory_id=str(uuid4()), user_id=user_id, access_count=0, content=content
        )
        self._memory_upsert(new_memory)

    @kernel_function(description="Update an existing memory with new content")
    def memory_update(self, memory_id: str, new_content: str) -> None:
        memory = self._get_memory_by_id(memory_id)
        if memory is None:
            return
        memory.content = new_content
        self._memory_upsert(memory)

    @kernel_function(description="Search for memories for a specific user")
    def memory_search(self, user_id: str, query: str) -> List[Memory]:
        query_embeddings = self._generate_embeddings(query)

        query_result = self.qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embeddings,
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id", match=models.MatchValue(value=user_id)
                    )
                ]
            ),
            score_threshold=SCORE_THRESHOLD,
            limit=RECALL_LIMIT,
        )
        return [Memory.model_validate(point.payload) for point in query_result.points]

    def _check_create_memory_collection(self) -> None:
        try:
            self.qdrant.get_collection(COLLECTION_NAME)
        except UnexpectedResponse:
            self.qdrant.create_collection(
                COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    distance=models.Distance.COSINE, size=VECTOR_SIZE
                ),
            )

    def _generate_embeddings(self, content) -> List[float]:
        embedding = self.client.embeddings.create(model=EMBEDDING_MODEL, input=content)
        return embedding.data[0].embedding

    def _memory_upsert(self, memory: Memory) -> None:
        embeddings = self._generate_embeddings(memory.content)
        self.qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=memory.memory_id, vector=embeddings, payload=memory.model_dump()
                )
            ],
        )

    def _get_memory_by_id(self, memory_id: str) -> Memory | None:
        result = self.qdrant.retrieve(collection_name=COLLECTION_NAME, ids=[memory_id])
        if len(result) < 1:
            return None
        return Memory.model_validate(result[0].payload)
