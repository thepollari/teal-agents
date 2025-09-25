import json

from langchain_core.chat_history import BaseChatMessageHistory
from ska_utils import AppConfig

from sk_agents.configs import TA_STRUCTURED_OUTPUT_TRANSFORMER_MODEL
from sk_agents.ska_types import InvokeResponse, TokenUsage
from sk_agents.skagents.kernel_builder import ChainBuilder
from sk_agents.type_loader import get_type_loader


class OutputTransformer:
    NAME = "structured-output"
    SYSTEM_PROMPT = (
        "Convert the given text into a structured output. Do not summarize or paraphrase the text."
    )

    def __init__(self, chain_builder: ChainBuilder):
        self.chain_builder = chain_builder

    async def transform_output(self, output: str, output_type_str: str) -> InvokeResponse:
        type_loader = get_type_loader()
        output_type = type_loader.get_type(output_type_str)

        app_config = AppConfig()
        structured_output_model = app_config.get(TA_STRUCTURED_OUTPUT_TRANSFORMER_MODEL.env_name)

        agent_executor = self.chain_builder.build_chain(
            model_name=structured_output_model,
            service_id=self.NAME,
            system_prompt=self.SYSTEM_PROMPT,
            plugins=[],
            remote_plugins=[],
        )

        history = BaseChatMessageHistory()
        history.add_user_message(output)

        result = await agent_executor.ainvoke({
            "input": output,
            "chat_history": history.messages
        })

        content = result["output"]
        if content:
            try:
                data = json.loads(content)
                return InvokeResponse(
                    token_usage=TokenUsage(
                        completion_tokens=0,  # LangChain token usage tracking differs
                        prompt_tokens=0,
                        total_tokens=0,
                    ),
                    output_raw=output,
                    output_pydantic=output_type(**data),
                )
            except json.JSONDecodeError:
                return InvokeResponse(
                    token_usage=TokenUsage(
                        completion_tokens=0,
                        prompt_tokens=0,
                        total_tokens=0,
                    ),
                    output_raw=output,
                    output_pydantic=output_type(),
                )
