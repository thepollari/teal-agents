from ska_utils import Config

TA_AGW_KEY = Config(env_name="TA_AGW_KEY", is_required=True, default_value=None)
TA_AGW_HOST = Config(
    env_name="TA_AGW_HOST", is_required=True, default_value="localhost:8000"
)
TA_AGW_SECURE = Config(
    env_name="TA_AGW_SECURE", is_required=True, default_value="false"
)
TA_SERVICE_CONFIG = Config(
    env_name="TA_SERVICE_CONFIG", is_required=True, default_value="conf/config.yaml"
)
TA_AUTH_ENABLED = Config(
    env_name="TA_AUTH_ENABLED", is_required=True, default_value="false"
)
TA_SERVICES_TYPE = Config(
    env_name="TA_SERVICES_TYPE", is_required=True, default_value="internal"
)
TA_SERVICES_ENDPOINT = Config(
    env_name="TA_SERVICES_ENDPOINT", is_required=False, default_value=None
)
TA_SERVICES_TOKEN = Config(
    env_name="TA_SERVICES_TOKEN", is_required=False, default_value=None
)

CONFIGS = [
    TA_AGW_KEY,
    TA_AGW_HOST,
    TA_AGW_SECURE,
    TA_SERVICE_CONFIG,
    TA_AUTH_ENABLED,
    TA_SERVICES_TYPE,
    TA_SERVICES_ENDPOINT,
    TA_SERVICES_TOKEN,
]
