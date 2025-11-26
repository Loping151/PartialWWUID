from gsuid_core.utils.plugins_config.gs_config import StringConfig

from ..utils.resource.RESOURCE_PATH import CONFIG_PATH, MAIN_PATH
from .config_default import CONFIG_DEFAULT
from .show_config import SHOW_CONIFG

WutheringWavesConfig = StringConfig(
    "WutheringWavesUID",
    CONFIG_PATH,
    CONFIG_DEFAULT,
)

ShowConfig = StringConfig(
    "鸣潮展示配置",
    MAIN_PATH / "show_config.json",
    SHOW_CONIFG,
)
