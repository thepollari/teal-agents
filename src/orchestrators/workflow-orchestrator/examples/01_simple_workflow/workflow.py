import logging
from dataclasses import dataclass

from dapr.ext.workflow import DaprWorkflowContext, WorkflowActivityContext

from workflow_orchestrator import Workflow


@dataclass
class DemoWorkflowInput:
    name: str
    message: str


class DemoWorkflow(Workflow):
    @staticmethod
    def setup():
        pass

    @staticmethod
    def entrypoint(ctx: DaprWorkflowContext, workflow_input: DemoWorkflowInput):
        yield ctx.call_activity(function1, input=workflow_input)
        yield ctx.call_activity(function2, input=workflow_input)


def function1(ctx: WorkflowActivityContext, param: DemoWorkflowInput):
    logger = logging.getLogger("function1")
    logger.info(f"Hello, {param.name}! - {param.message}")


def function2(ctx: WorkflowActivityContext, param: DemoWorkflowInput):
    logger = logging.getLogger("function2")
    logger.info(f"Hello, {param.name}! - {param.message}")
