from typing import Dict

from gsuid_core.data_store import get_res_path
from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsBoolConfig,
    GsImageConfig,
    GsIntConfig,
    GsStrConfig,
)

bg_path = get_res_path(["WutheringWavesUID", "bg"])

SHOW_CONIFG: Dict[str, GSC] = {
    "BlurRadius": GsIntConfig(
        "毛玻璃半径越大，毛玻璃效果越明显，0为不开启",
        "毛玻璃半径越大，毛玻璃效果越明显",
        0,
        100,
    ),
    "BlurBrightness": GsStrConfig(
        "毛玻璃亮度",
        "毛玻璃亮度",
        "1.2",
        ["0.9", "1.0", "1.1", "1.2", "1.3", "1.4", "1.5"],
    ),
    "BlurContrast": GsStrConfig(
        "毛玻璃对比度",
        "毛玻璃对比度",
        "0.9",
        ["0.8", "0.85", "0.9", "0.95", "1.0", "1.05", "1.1"],
    ),
    "CardBg": GsBoolConfig(
        "是否开启自定义面板背景",
        "开启路径位于WutheringWavesUID/bg",
        False,
    ),
    "CardBgPath": GsImageConfig(
        "自定义面板背景",
        "自定义面板背景图片",
        str(bg_path / "card.jpg"),
        str(bg_path),
        "card",
        "jpg",
    ),
}
