from ska_utils import Config

TA_API_KEY = Config(env_name="TA_API_KEY", is_required=True, default_value=None)
TA_SERVICE_CONFIG = Config(
    env_name="TA_SERVICE_CONFIG", is_required=True, default_value="agents/config.yaml"
)
TA_REMOTE_PLUGIN_PATH = Config(
    env_name="TA_REMOTE_PLUGIN_PATH", is_required=False, default_value=None
)
TA_TYPES_MODULE = Config(
    env_name="TA_TYPES_MODULE", is_required=False, default_value=None
)
TA_PLUGIN_MODULE = Config(
    env_name="TA_PLUGIN_MODULE", is_required=False, default_value=None
)
TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE = Config(
    env_name="TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE",
    is_required=False,
    default_value=None,
)
TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME = Config(
    env_name="TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME",
    is_required=False,
    default_value=None,
)
TA_STRUCTURED_OUTPUT_TRANSFORMER_MODEL = Config(
    env_name="TA_STRUCTURED_OUTPUT_TRANSFORMER_MODEL",
    is_required=False,
    default_value="gpt-4o",
)
TA_A2A_ENABLED = Config(
    env_name="TA_A2A_ENABLED", is_required=True, default_value="false"
)
TA_AGENT_BASE_URL = Config(
    env_name="TA_AGENT_BASE_URL",
    is_required=True,
    default_value="http://localhost:8000",
)
TA_PROVIDER_ORG = Config(
    env_name="TA_PROVIDER_ORG", is_required=True, default_value="My Organization"
)
TA_PROVIDER_URL = Config(
    env_name="TA_PROVIDER_URL", is_required=True, default_value="http://localhost:8000"
)


configs: list[Config] = [
    TA_API_KEY,
    TA_SERVICE_CONFIG,
    TA_REMOTE_PLUGIN_PATH,
    TA_TYPES_MODULE,
    TA_PLUGIN_MODULE,
    TA_CUSTOM_CHAT_COMPLETION_FACTORY_MODULE,
    TA_CUSTOM_CHAT_COMPLETION_FACTORY_CLASS_NAME,
    TA_STRUCTURED_OUTPUT_TRANSFORMER_MODEL,
    TA_A2A_ENABLED,
    TA_AGENT_BASE_URL,
    TA_PROVIDER_ORG,
    TA_PROVIDER_URL,
]
