import logging
import os

from dapr.ext.workflow import WorkflowRuntime
from fastapi import FastAPI, HTTPException
from pydantic_yaml import parse_yaml_file_as
from ska_utils import AppConfig
from ska_utils import get_telemetry, initialize_telemetry

from workflow_orchestrator import WorkflowClient, WorkflowNotFoundException
from workflow_orchestrator.configs import (
    configs,
    TA_SERVICE_CONFIG,
    TA_WORKFLOW_MODULE,
)
from workflow_orchestrator.middleware import TelemetryMiddleware
from workflow_orchestrator.wf_types import (
    Config,
    ScheduleWorkflowResponse,
    WorkflowState,
    WorkflowEvent,
    WorkflowUpdateRequest,
)
from workflow_orchestrator.workflow_loader import get_workflow_loader


def docstring_parameter(*sub):
    def dec(obj):
        obj.__doc__ = obj.__doc__.format(*sub)
        return obj

    return dec


logging.basicConfig(level=logging.DEBUG)

AppConfig.add_configs(configs)
app_config = AppConfig()

config_file = app_config.get(TA_SERVICE_CONFIG.env_name)
config: Config = parse_yaml_file_as(Config, config_file)

workflow_path = str(os.path.dirname(config_file))

workflow_module = app_config.get(TA_WORKFLOW_MODULE.env_name)
if workflow_module is None:
    workflow_file = os.path.join(workflow_path, "workflow.py")
    if os.path.exists(workflow_path):
        app_config.props[TA_WORKFLOW_MODULE.env_name] = workflow_file
        workflow_module = workflow_file
    else:
        raise ValueError("Workflow module not found")

initialize_telemetry(f"{config.service_name}-{config.version}", app_config)

workflow_loader = get_workflow_loader(workflow_module)
workflow_class = workflow_loader.get_workflow_object(config.entrypoint)
input_type = workflow_loader.get_workflow_object(config.input_type)
activity_functions = workflow_loader.find_activity_function()

if not config.description:
    config.description = f"Workflow for {config.service_name}"

wfr = WorkflowRuntime()
wfr.register_workflow(workflow_class.entrypoint)
for activity_function in activity_functions:
    wfr.register_activity(activity_function)
wfr.start()

app = FastAPI()
# noinspection PyTypeChecker
app.add_middleware(TelemetryMiddleware, get_telemetry())

workflow_class.setup()


@app.post(f"/{config.service_name}/{str(config.version)}")
@docstring_parameter(config.description)
async def invoke(inputs: input_type) -> ScheduleWorkflowResponse:
    """
    {0}
    """
    client = WorkflowClient()

    return client.schedule_new_workflow(workflow_class.entrypoint, inputs)


@app.get(
    f"/{config.service_name}/{str(config.version)}/{{instance_id}}",
    responses={404: {"description": "Workflow not found"}},
)
async def get_workflow(instance_id: str) -> WorkflowState:
    """
    Retrieve the workflow state by instance ID
    """
    client = WorkflowClient()

    try:
        return client.get_workflow_state(instance_id)
    except WorkflowNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post(
    f"/{config.service_name}/{str(config.version)}/{{instance_id}}/events",
    responses={404: {"description": "Workflow not found"}},
)
async def send_event(instance_id: str, event: WorkflowEvent) -> WorkflowState:
    """
    Send an event to a workflow instance
    """
    client = WorkflowClient()

    try:
        return client.raise_workflow_event(instance_id, event)
    except WorkflowNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.patch(
    f"/{config.service_name}/{str(config.version)}/{{instance_id}}",
    responses={404: {"description": "Workflow not found"}},
)
async def update_state(
    instance_id: str, update_request: WorkflowUpdateRequest
) -> WorkflowState:
    """
    Pause, Resume, or Terminate an existing workflow by instance ID
    """
    client = WorkflowClient()

    try:
        return client.update_state(instance_id, update_request)
    except WorkflowNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
