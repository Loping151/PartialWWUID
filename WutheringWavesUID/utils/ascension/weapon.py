import copy
from pathlib import Path
from typing import Optional, Union

from msgspec import json as msgjson

from gsuid_core.logger import logger

from ..ascension.constant import fixed_name
from .model import WeaponModel

MAP_PATH = Path(__file__).parent.parent / "map/detail_json/weapon"
weapon_id_data = {}


def read_weapon_json_files(directory):
    files = directory.rglob("*.json")

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = msgjson.decode(f.read())
                file_name = file.name.split(".")[0]
                weapon_id_data[file_name] = data
        except Exception as e:
            logger.exception(f"read_weapon_json_files load fail decoding {file}", e)


read_weapon_json_files(MAP_PATH)


class WavesWeaponResult:
    def __init__(self):
        self.name: str = ""
        self.starLevel: int = 4
        self.type: int = 0
        self.stats = []
        self.param = []
        self.effect: str = ""
        self.effectName: str = ""
        self.sub_effect = {}
        self.resonLevel: int = 1

    def get_resonLevel_name(self):
        return f"谐振{['一', '二', '三', '四', '五'][self.resonLevel - 1]}阶"


def get_breach(breach: Union[int, None], level: int):
    if breach is None:
        if level <= 20:
            breach = 0
        elif level <= 40:
            breach = 1
        elif level <= 50:
            breach = 2
        elif level <= 60:
            breach = 3
        elif level <= 70:
            breach = 4
        elif level <= 80:
            breach = 5
        elif level <= 90:
            breach = 6
    return breach


def get_weapon_detail(
    weapon_id: Union[str, int],
    level: int,
    breach: Union[int, None] = None,
    resonLevel: Union[int, None] = 1,
) -> WavesWeaponResult:
    """
    breach 突破
    resonLevel 精炼
    """
    result = WavesWeaponResult()
    if str(weapon_id) not in weapon_id_data:
        return result

    breach = get_breach(breach, level)

    weapon_data = weapon_id_data[str(weapon_id)]
    result.name = weapon_data["name"]
    result.starLevel = weapon_data["starLevel"]
    result.type = weapon_data["type"]
    result.effectName = weapon_data["effectName"]
    result.stats = copy.deepcopy(weapon_data["stats"][str(breach)][str(level)])
    result.param = weapon_data["param"]
    effect = weapon_data["effect"]
    if resonLevel is None:
        resonLevel = 1
    result.resonLevel = resonLevel
    for i, p in enumerate(weapon_data["param"]):
        _temp = "{" + str(i) + "}"
        effect = effect.replace(f"{_temp}", str(p[resonLevel - 1]))
    result.effect = effect

    for stat in result.stats:
        if stat["isPercent"]:
            stat["value"] = f"{stat['value'] / 100:.1f}%"
        elif stat["isRatio"]:
            stat["value"] = f"{stat['value'] * 100:.1f}%"
        else:
            stat["value"] = f"{int(stat['value'])}"

    result.sub_effect = {}
    for i, v in enumerate(fixed_name):
        if result.effect.startswith(v):
            value = weapon_data["param"][0][resonLevel - 1]
            name = v.replace("提升", "").replace("全", "")
            result.sub_effect = {"name": name, "value": f"{value}"}

    return result


def get_weapon_id(weapon_name):
    return next(
        (_id for _id, value in weapon_id_data.items() if value["name"] == weapon_name),
        None,
    )


def get_weapon_star(weapon_name) -> int:
    weapon_id = get_weapon_id(weapon_name)
    if weapon_id is None:
        return 4

    result = get_weapon_detail(weapon_id, 90)
    if result is None:
        return 4
    return result.starLevel


def get_weapon_model(weapon_id: Union[int, str]) -> Optional[WeaponModel]:
    if str(weapon_id) not in weapon_id_data:
        return None
    return WeaponModel(**weapon_id_data[str(weapon_id)])
