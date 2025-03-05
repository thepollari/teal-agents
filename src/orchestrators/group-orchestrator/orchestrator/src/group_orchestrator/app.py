from pydantic import BaseModel

class Agent:
    pass

class Task:
    pass

def execution_loop(overall_goal: str, available_agents: List[Agent], completed_tasks: List[Task]) -> None:
    # Input - Goal, list of agents, list of previously completed tasks with references to results
    pass