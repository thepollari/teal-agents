from collab_orchestrator.co_types import SpecBase


class TeamSpec(SpecBase):
    max_rounds: int
    manager_agent: str
