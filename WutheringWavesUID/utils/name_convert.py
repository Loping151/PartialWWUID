import json
from pathlib import Path
from typing import Dict, List, Optional

from msgspec import json as msgjson

from gsuid_core.logger import logger

from ..utils.resource.RESOURCE_PATH import (
    CUSTOM_CHAR_ALIAS_PATH,
    CUSTOM_ECHO_ALIAS_PATH,
    CUSTOM_SONATA_ALIAS_PATH,
    CUSTOM_WEAPON_ALIAS_PATH,
)

MAP_PATH = Path(__file__).parent / "map"
ALIAS_LIST = Path(__file__).parent / "alias"
CHAR_ALIAS = ALIAS_LIST / "char_alias.json"
WEAPON_ALIAS = ALIAS_LIST / "weapon_alias.json"
SONATA_ALIAS = ALIAS_LIST / "sonata_alias.json"
ECHO_ALIAS = ALIAS_LIST / "echo_alias.json"

char_alias_data: Dict[str, List[str]] = {}
weapon_alias_data: Dict[str, List[str]] = {}
sonata_alias_data: Dict[str, List[str]] = {}
echo_alias_data: Dict[str, List[str]] = {}


def add_dictionaries(dict1, dict2):
    all_keys = set(dict1.keys()) | set(dict2.keys())
    return {key: list(set(dict1.get(key, []) + dict2.get(key, []))) for key in all_keys}


def load_alias_data():
    global char_alias_data, weapon_alias_data, sonata_alias_data, echo_alias_data
    with open(CHAR_ALIAS, "r", encoding="UTF-8") as f:
        char_alias_data = msgjson.decode(f.read(), type=Dict[str, List[str]])

    with open(WEAPON_ALIAS, "r", encoding="UTF-8") as f:
        weapon_alias_data = msgjson.decode(f.read(), type=Dict[str, List[str]])

    with open(SONATA_ALIAS, "r", encoding="UTF-8") as f:
        sonata_alias_data = msgjson.decode(f.read(), type=Dict[str, List[str]])

    with open(ECHO_ALIAS, "r", encoding="UTF-8") as f:
        echo_alias_data = msgjson.decode(f.read(), type=Dict[str, List[str]])

    if CUSTOM_CHAR_ALIAS_PATH.exists():
        try:
            with open(CUSTOM_CHAR_ALIAS_PATH, "r", encoding="UTF-8") as f:
                custom_char_alias_data = msgjson.decode(
                    f.read(), type=Dict[str, List[str]]
                )
        except Exception as e:
            logger.exception(f"读取自定义角色别名失败 {CUSTOM_CHAR_ALIAS_PATH} - {e}")
            custom_char_alias_data = {}

        char_alias_data = add_dictionaries(char_alias_data, custom_char_alias_data)

    if CUSTOM_SONATA_ALIAS_PATH.exists():
        try:
            with open(CUSTOM_SONATA_ALIAS_PATH, "r", encoding="UTF-8") as f:
                custom_sonata_alias_data = msgjson.decode(
                    f.read(), type=Dict[str, List[str]]
                )
        except Exception as e:
            logger.exception(f"读取自定义合鸣别名失败 {CUSTOM_SONATA_ALIAS_PATH} - {e}")
            custom_sonata_alias_data = {}

        sonata_alias_data = add_dictionaries(
            sonata_alias_data, custom_sonata_alias_data
        )

    if CUSTOM_WEAPON_ALIAS_PATH.exists():
        try:
            with open(CUSTOM_WEAPON_ALIAS_PATH, "r", encoding="UTF-8") as f:
                custom_weapon_alias_data = msgjson.decode(
                    f.read(), type=Dict[str, List[str]]
                )
        except Exception as e:
            logger.exception(f"读取自定义武器别名失败 {CUSTOM_WEAPON_ALIAS_PATH} - {e}")
            custom_weapon_alias_data = {}

        weapon_alias_data = add_dictionaries(
            weapon_alias_data, custom_weapon_alias_data
        )

    if CUSTOM_ECHO_ALIAS_PATH.exists():
        try:
            with open(CUSTOM_ECHO_ALIAS_PATH, "r", encoding="UTF-8") as f:
                custom_echo_alias_data = msgjson.decode(
                    f.read(), type=Dict[str, List[str]]
                )
        except Exception as e:
            logger.exception(f"读取自定义声骸别名失败 {CUSTOM_ECHO_ALIAS_PATH} - {e}")
            custom_echo_alias_data = {}

        echo_alias_data = add_dictionaries(echo_alias_data, custom_echo_alias_data)

    with open(CUSTOM_CHAR_ALIAS_PATH, "w", encoding="UTF-8") as f:
        f.write(json.dumps(char_alias_data, indent=2, ensure_ascii=False))

    with open(CUSTOM_SONATA_ALIAS_PATH, "w", encoding="UTF-8") as f:
        f.write(json.dumps(sonata_alias_data, indent=2, ensure_ascii=False))

    with open(CUSTOM_WEAPON_ALIAS_PATH, "w", encoding="UTF-8") as f:
        f.write(json.dumps(weapon_alias_data, indent=2, ensure_ascii=False))

    with open(CUSTOM_ECHO_ALIAS_PATH, "w", encoding="UTF-8") as f:
        f.write(json.dumps(echo_alias_data, indent=2, ensure_ascii=False))


load_alias_data()

with open(MAP_PATH / "CharId2Data.json", "r", encoding="UTF-8") as f:
    char_id_data = msgjson.decode(f.read(), type=Dict[str, Dict[str, str]])

with open(MAP_PATH / "id2name.json", "r", encoding="UTF-8") as f:
    id2name = msgjson.decode(f.read(), type=Dict[str, str])


def alias_to_char_name(char_name: str) -> str:
    for i in char_alias_data:
        if (char_name in i) or (char_name in char_alias_data[i]):
            return i
    return char_name


def alias_to_char_name_optional(char_name: Optional[str]) -> Optional[str]:
    if not char_name:
        return None
    for i in char_alias_data:
        if (char_name in i) or (char_name in char_alias_data[i]):
            return i
    return None


def alias_to_char_name_list(char_name: str) -> List[str]:
    for i in char_alias_data:
        if (char_name in i) or (char_name in char_alias_data[i]):
            return char_alias_data[i]
    return []


def char_id_to_char_name(char_id: str) -> Optional[str]:
    char_id = str(char_id)
    if char_id in char_id_data:
        return char_id_data[char_id]["name"]
    else:
        return None


def char_name_to_char_id(char_name: str) -> Optional[str]:
    char_name = alias_to_char_name(char_name)
    for id, name in id2name.items():
        if char_name == name:
            return id
    else:
        return None


def alias_to_weapon_name(weapon_name: str) -> str:
    for i in weapon_alias_data:
        if (weapon_name in i) or (weapon_name in weapon_alias_data[i]):
            return i

    if "专武" in weapon_name:
        char_name = weapon_name.replace("专武", "")
        name = alias_to_char_name(char_name)
        weapon_name = f"{name}专武"

    for i in weapon_alias_data:
        if (weapon_name in i) or (weapon_name in weapon_alias_data[i]):
            return i

    return weapon_name


def weapon_name_to_weapon_id(weapon_name: str) -> Optional[str]:
    weapon_name = alias_to_weapon_name(weapon_name)
    for id, name in id2name.items():
        if weapon_name == name:
            return id
    else:
        return None


def alias_to_sonata_name(sonata_name: str | None) -> str | None:
    if sonata_name is None:
        return None
    for i in sonata_alias_data:
        if (sonata_name in i) or (sonata_name in sonata_alias_data[i]):
            return i
    return None


def alias_to_echo_name(echo_name: str) -> str:
    for i, j in echo_alias_data.items():
        if echo_name == i:
            return i
        if echo_name in j:
            return i
        for k in j:
            if k and echo_name in k:
                return i
        if echo_name in i:
            return i
    return echo_name


def echo_name_to_echo_id(echo_name: str) -> Optional[str]:
    echo_name = alias_to_echo_name(echo_name)
    for id, name in id2name.items():
        if echo_name == name:
            return id
    else:
        return None


def easy_id_to_name(id: str, default: str = "") -> str:
    return id2name.get(id, default)


def get_all_char_id() -> List[str]:
    return list(char_id_data.keys())
