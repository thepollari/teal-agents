from enum import Enum
from typing import List

from group_orchestrator.types.tasks import Task


class StepStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    COMPLETED = "COMPLETED"


class Step:
    step_number: int
    step_tasks: List[Task]
    step_status: StepStatus
