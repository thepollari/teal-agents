from dataclasses import dataclass
from typing import List

from dapr.ext.workflow import DaprWorkflowContext
from durabletask.client import OrchestrationStatus

from workflow_orchestrator import (
    DataClass,
    Workflow,
    AgentActivityInput,
    invoke_agent_task,
    create_agent_input,
)


@dataclass
class Memory:
    memory_id: str
    user_id: str
    access_count: int
    content: str


@dataclass
class InteractionInput(DataClass):
    user_id: str
    message: str
    response: str


@dataclass
class MemorizerInput(DataClass):
    user_id: str
    message: str
    response: str
    memories: List[Memory]


@dataclass
class MemoryList(DataClass):
    memories: List[Memory]


class AgentWorkflow(Workflow):
    @staticmethod
    def setup():
        pass

    @staticmethod
    def entrypoint(ctx: DaprWorkflowContext, workflow_input: InteractionInput):
        # 1. Format the input for the agent activity by calling `create_agent_input`
        recall_activity_input: AgentActivityInput[InteractionInput, MemoryList] = (
            create_agent_input("RecallAgent", "0.1", workflow_input, MemoryList)
        )
        # 2. Invoke the agent by calling the `invoke_agent_task` activity
        memory_list = yield ctx.call_activity(
            invoke_agent_task, input=recall_activity_input
        )

        # 3. Leverage the output from the first task for the second task
        memorizer_input = MemorizerInput(
            workflow_input.user_id,
            workflow_input.message,
            workflow_input.response,
            memory_list.memories,
        )
        # 4. Format the input for the memorizer activity by calling `create_agent_input`
        memorize_activity_input: AgentActivityInput[MemorizerInput, str] = (
            create_agent_input("MemorizerAgent", "0.1", memorizer_input)
        )
        # 5. Invoke the agent by calling the `invoke_agent_task` activity
        result = yield ctx.call_activity(
            invoke_agent_task, input=memorize_activity_input
        )
        return result
