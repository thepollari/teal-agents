from enum import Enum
from typing import Literal, List, Optional

import aiohttp
from pydantic import BaseModel

from group_orchestrator.agents.aio_invokable_agent import AioInvokableAgent


class ContentType(Enum):
    IMAGE = "image"
    TEXT = "text"


class MultiModalItem(BaseModel):
    content_type: ContentType
    content: str


class HistoryMultiModalMessage(BaseModel):
    role: Literal["user", "assistant"]
    items: List[MultiModalItem]


class BaseMultiModalInput(BaseModel):
    chat_history: Optional[List[HistoryMultiModalMessage]] = None


class PreRequisite(BaseModel):
    goal: str
    result: str


class AioTaskAgent(AioInvokableAgent):
    @staticmethod
    def _pre_requisite_to_item(
        pre_requisite: PreRequisite,
    ) -> List[HistoryMultiModalMessage]:
        user_message = HistoryMultiModalMessage(
            role="user",
            items=[
                MultiModalItem(
                    content_type=ContentType.TEXT, content=pre_requisite.goal
                )
            ],
        )
        assistant_message = HistoryMultiModalMessage(
            role="assistant",
            items=[
                MultiModalItem(
                    content_type=ContentType.TEXT, content=pre_requisite.result
                )
            ],
        )
        return [user_message, assistant_message]

    @staticmethod
    def _build_chat_history(
        goal: str, pre_reqs: List[PreRequisite] | None = None
    ) -> BaseMultiModalInput:
        chat_history_messages: List[HistoryMultiModalMessage] = []
        for pre_req in pre_reqs:
            chat_history_messages.extend(AioTaskAgent._pre_requisite_to_item(pre_req))
        chat_history_messages.append(
            HistoryMultiModalMessage(
                role="user",
                items=[MultiModalItem(content_type=ContentType.TEXT, content=goal)],
            )
        )
        return BaseMultiModalInput(chat_history=chat_history_messages)

    async def perform_task(
        self,
        session: aiohttp.ClientSession,
        goal: str,
        pre_requisites: List[PreRequisite] | None = None,
    ) -> str:
        chat_history = AioTaskAgent._build_chat_history(goal, pre_requisites)
        print("----------")
        print(f"Invoking Agent: {self.agent.name}")
        print(f"Request:        {goal}")
        print(f"Pre-requisites: {pre_requisites}")
        response = await self.invoke(session, chat_history)
        print(f"Response:       {response['output_raw']}")
        print("----------")
        return response["output_raw"]
