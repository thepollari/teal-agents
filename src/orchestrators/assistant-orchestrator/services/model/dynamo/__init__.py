from ska_utils import AppConfig

from configs import CONFIGS, TA_DYNAMO_HOST, TA_DYNAMO_REGION, TA_DYNAMO_TABLE_PREFIX

AppConfig.add_configs(CONFIGS)


def _get_host() -> str:
    return AppConfig().get(TA_DYNAMO_HOST.env_name)


def _get_region() -> str:
    return AppConfig().get(TA_DYNAMO_REGION.env_name)


def _get_table_name(suffix: str) -> str:
    return f"{AppConfig().get(TA_DYNAMO_TABLE_PREFIX.env_name)}{suffix}"
