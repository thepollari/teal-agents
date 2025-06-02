from pydantic import BaseModel

from collab_orchestrator.agents import PreRequisite
from collab_orchestrator.team_handler.manager_agent import ConversationMessage


class Conversation(BaseModel):
    messages: list[ConversationMessage]

    def to_pre_requisites(self) -> list[PreRequisite]:
        pre_requisites: list[PreRequisite] = []
        for message in self.messages:
            prereq_goal = (
                f"Task '{message.task_id}' goal for agent {message.agent_name}:"
                f"\n\n{message.instructions}"
            )
            prereq_result = (
                f"Task '{message.task_id}' result from agent {message.agent_name}:"
                f"\n\n{message.result}"
            )
            pre_requisites.append(PreRequisite(goal=prereq_goal, result=prereq_result))
        return pre_requisites

    def add_item(self, task_id: str, agent_name: str, instructions: str, result: str):
        self.messages.append(
            ConversationMessage(
                task_id=task_id,
                agent_name=agent_name,
                instructions=instructions,
                result=result,
            )
        )

    def get_message_by_task_id(self, task_id: str) -> ConversationMessage | None:
        for message in self.messages:
            if message.task_id == task_id:
                return message
        return None
