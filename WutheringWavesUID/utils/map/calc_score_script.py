import copy
import json
import math
from pathlib import Path
from typing import List, Optional

from msgspec import json as msgjson

SCRIPT_PATH = Path(__file__).parents[0]
MAP_PATH = SCRIPT_PATH / "character"
DETAIL_PATH = SCRIPT_PATH / "detail_json"
CHAR_DETAIL_PATH = DETAIL_PATH / "char"
WEAPON_DETAIL_PATH = DETAIL_PATH / "weapon"
SONATA_DETAIL_PATH = DETAIL_PATH / "sonata"


LIMIT_DATA_PATH = SCRIPT_PATH / "limit.json"
TEMPLATE_DATA_PATH = SCRIPT_PATH / "templata.json"
ROLE_LIMIT_PATH = SCRIPT_PATH / "1.json"
ID_NAME_PATH = SCRIPT_PATH / "id2name.json"

limit_data = json.loads(LIMIT_DATA_PATH.read_text(encoding="utf-8"))
template_data = json.loads(TEMPLATE_DATA_PATH.read_text(encoding="utf-8"))
id2Name = json.loads(ID_NAME_PATH.read_text(encoding="utf-8"))


# 声骸副词条
phantom_sub_value = [
    {"name": "攻击", "values": ["30", "40", "50", "60"]},
    {
        "name": "攻击%",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "生命",
        "values": ["320", "360", "390", "430", "470", "510", "540", "580"],
    },
    {
        "name": "生命%",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {"name": "防御", "values": ["40", "50", "60", "70"]},
    {
        "name": "防御%",
        "values": ["8.1%", "9%", "10%", "10.9%", "11.8%", "12.8%", "13.8%", "14.7%"],
    },
    {
        "name": "暴击",
        "values": ["6.3%", "6.9%", "7.5%", "8.1%", "8.7%", "9.3%", "9.9%", "10.5%"],
    },
    {
        "name": "暴击伤害",
        "values": [
            "12.6%",
            "13.8%",
            "15%",
            "16.2%",
            "17.4%",
            "18.6%",
            "19.8%",
            "21.0%",
        ],
    },
    {
        "name": "普攻伤害加成",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "重击伤害加成",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "共鸣技能伤害加成",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "共鸣解放伤害加成",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "技能伤害加成",
        "values": [
            "6%",
            "6.4%",
            "7.1%",
            "7.9%",
            "8.6%",
            "9.4%",
            "10.1%",
            "10.9%",
            "11.6%",
        ],
    },
    {
        "name": "共鸣效率",
        "values": ["6.8%", "7.6%", "8.4%", "9.2%", "10%", "10.8%", "11.6%", "12.4%"],
    },
]
phantom_sub_value_map = {i["name"]: i["values"] for i in phantom_sub_value}

# 1, 3, 4
phantom_main_value = [
    {"name": "攻击", "values": ["0", "100", "150"]},
    {"name": "攻击%", "values": ["18%", "30%", "33%"]},
    {"name": "生命", "values": ["2280", "0", "0"]},
    {"name": "生命%", "values": ["22.8%", "30%", "33%"]},
    {"name": "防御%", "values": ["18%", "38%", "41.8%"]},
    {"name": "暴击", "values": ["0%", "0%", "22%"]},
    {"name": "暴击伤害", "values": ["0%", "0%", "44%"]},
    {"name": "共鸣效率", "values": ["0%", "32%", "0%"]},
    {"name": "属性伤害加成", "values": ["0%", "30%", "0%"]},
    {"name": "治疗效果加成", "values": ["0%", "0%", "26.4%"]},
]
phantom_main_value_map = {i["name"]: i["values"] for i in phantom_main_value}


def calc_sub_max_score(
    _temp, sub_props, jineng: Optional[List] = None, skill_weight: Optional[List] = None
):
    score = 0
    jineng_list = [
        "普攻伤害加成",
        "重击伤害加成",
        "共鸣技能伤害加成",
        "共鸣解放伤害加成",
    ]
    for i in _temp:
        ratio = 1
        if jineng is not None and i == "技能伤害加成":
            ratio = jineng
        elif i in jineng_list:
            if skill_weight is not None:
                ratio = skill_weight[jineng_list.index(i)]
        _phantom_value = phantom_sub_value_map[i][-1]
        if "%" in _phantom_value:
            _phantom_value = _phantom_value.replace("%", "")
        _phantom_value = float(_phantom_value)
        score += sub_props[i] * _phantom_value * ratio

    # return round(score, 2)
    return math.floor(score * 1000) / 1000


def calc_main_max_score(_temp, main_props):
    score = []
    for k, v in _temp.items():
        cost = int(k.split(".")[0])
        if cost == 4:
            index = 2
        elif cost == 3:
            index = 1
        else:
            index = 0
        _score = 0
        for i in v:
            _phantom_value = phantom_main_value_map[i][index]
            if "%" in _phantom_value:
                _phantom_value = _phantom_value.replace("%", "")
            _phantom_value = float(_phantom_value)
            _score += main_props.get(str(cost)).get(i, 0) * _phantom_value

        # score.append(round(_score, 2))
        score.append(math.floor(_score * 1000) / 1000)

    return score


def read_calc_json_files(directory):
    files = directory.rglob("calc*.json")

    char_limit_cards = []
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = msgjson.decode(f.read())

                skill_weight = data["skill_weight"]
                jineng = max(skill_weight)
                sub_max = calc_sub_max_score(
                    data["max_sub_props"], data["sub_props"], jineng, skill_weight
                )
                main_max = calc_main_max_score(
                    data["max_main_props"], data["main_props"]
                )
                # score_max = [round(sub_max + i, @) for i in main_max]
                score_max = [math.floor((sub_max + i) * 1000) / 1000 for i in main_max]

                print(
                    f"{file.parents[0].name}/{file.name} - 技能分: {jineng} - "
                    f"副词条最大: {sub_max} - "
                    f"主词条最大: {main_max} - "
                    f"总词条分数：{score_max}"
                )
                data["score_max"] = score_max
                data["total_grade"] = [0, 0.48, 0.6, 0.7, 0.78, 0.84]
                data["props_grade"] = [
                    [0, 0.48, 0.6, 0.7, 0.78, 0.84],
                    [0, 0.48, 0.6, 0.7, 0.78, 0.84],
                    [0, 0.48, 0.6, 0.7, 0.78, 0.84],
                ]
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            char_name = f"{file.parents[0].name}"
            char_limit = next(
                (
                    i
                    for i in limit_data["charList"]
                    if i["name"] == char_name and i["calcFile"] == file.name
                ),
                None,
            )
            if char_limit is None:
                continue
            card_limit = calc_char_limit(char_limit, data)
            if card_limit:
                char_limit_cards.append(card_limit)
        except Exception as e:
            print(f"Error decoding {file}", e)

    with open(ROLE_LIMIT_PATH, "w", encoding="utf-8") as f:
        json.dump(char_limit_cards, f, ensure_ascii=False, indent=2)


def calc_char_limit(char_limit, calc_file_dict):
    sonata_lib = next(
        (i for i in limit_data["sonataLib"] if i["libId"] == char_limit["sonataLibId"]),
        None,
    )
    if sonata_lib is None:
        return
    char_detail_path = CHAR_DETAIL_PATH / f"{char_limit['charId']}.json"
    if not char_detail_path.exists():
        return
    weapon_detail_path = WEAPON_DETAIL_PATH / f"{char_limit['weaponId']}.json"
    if not weapon_detail_path.exists():
        return
    char_detail = json.loads(char_detail_path.read_text(encoding="utf-8"))
    weapon_detail = json.loads(weapon_detail_path.read_text(encoding="utf-8"))

    char_template_data = copy.deepcopy(template_data)

    # 命座
    for i, j in zip(char_detail["chains"].values(), char_template_data["chainList"]):
        j["name"] = i["name"]
        j["description"] = i["desc"].format(*i["param"])
        j["iconUrl"] = ""
        j["unlocked"] = True

    # 技能
    skill_map = {
        "常态攻击": "1",
        "共鸣技能": "2",
        "共鸣回路": "7",
        "共鸣解放": "3",
        "变奏技能": "6",
        "延奏技能": "8",
    }
    for i in char_template_data["skillList"]:
        temp_skill = i["skill"]
        skill_type = temp_skill["type"]
        skill_detail = char_detail["skillTree"][skill_map[skill_type]]["skill"]

        temp_skill["name"] = skill_detail["name"]
        temp_skill["description"] = skill_detail["desc"].format(*skill_detail["param"])
        temp_skill["iconUrl"] = ""

    # role
    attributeIdMap = {1: "冷凝", 2: "热熔", 3: "导电", 4: "气动", 5: "衍射", 6: "湮灭"}
    weaponTypeIdMap = {1: "长刃", 2: "迅刀", 3: "佩枪", 4: "臂铠", 5: "音感仪"}
    temp_role = char_template_data["role"]
    temp_role["roleName"] = char_detail["name"]
    temp_role["iconUrl"] = ""
    temp_role["roleId"] = char_limit["charId"]
    temp_role["starLevel"] = char_detail["starLevel"]
    temp_role["weaponTypeId"] = char_detail["weaponTypeId"]
    temp_role["weaponTypeName"] = weaponTypeIdMap[char_detail["weaponTypeId"]]
    temp_role["attributeId"] = char_detail["attributeId"]
    temp_role["attributeName"] = attributeIdMap[char_detail["attributeId"]]

    # 武器
    temp_weapon = char_template_data["weaponData"]["weapon"]
    temp_weapon["weaponEffectName"] = weapon_detail["effect"].format(
        *[i[-1] for i in weapon_detail["param"]]
    )
    temp_weapon["weaponIcon"] = ""
    temp_weapon["weaponId"] = char_limit["weaponId"]
    temp_weapon["weaponName"] = weapon_detail["name"]
    temp_weapon["weaponStarLevel"] = weapon_detail["starLevel"]
    temp_weapon["weaponType"] = weapon_detail["type"]

    # 声骸

    attribute = char_template_data["role"]["attributeName"]

    list_index = 0

    fetterList = sonata_lib["fetterList"]
    for fetter in fetterList:
        sonata_detail_path = SONATA_DETAIL_PATH / f"{fetter['fetterDetailName']}.json"
        if not sonata_detail_path.exists():
            continue
        sonata_detail = json.loads(sonata_detail_path.read_text(encoding="utf-8"))

        temp_fetter_detail = {
            "firstDescription": "",
            "groupId": 0,
            "iconUrl": "",
            "name": sonata_detail["name"],
            "num": len(fetter["equipPhantomList"]),
            "secondDescription": "",
        }

        for j in fetter["equipPhantomList"]:
            i = char_template_data["phantomData"]["equipPhantomList"][list_index]
            cost = j["cost"]
            i["fetterDetail"] = temp_fetter_detail
            i["cost"] = cost
            phantomProp = i["phantomProp"]
            phantomProp["phantomId"] = j["phantomId"]
            phantomProp["name"] = id2Name[str(j["phantomId"])]
            phantomProp["cost"] = cost

            custom_main_shuxing = j.get("mainPropName")

            mainProps = i["mainProps"]
            for flag, main_props_name in enumerate(
                calc_file_dict["max_main_props"][f"{cost}.1"]
            ):
                if cost == 4:
                    index = 2
                elif cost == 3:
                    index = 1
                else:
                    index = 0
                if flag == 0 and custom_main_shuxing:
                    main_props_name = custom_main_shuxing
                _phantom_value = phantom_main_value_map[main_props_name][index]
                if main_props_name.startswith("属性"):
                    main_props_name = f"{attribute}伤害加成"
                res = {
                    "attributeName": main_props_name.replace("%", ""),
                    "attributeValue": _phantom_value,
                    "iconUrl": "",
                }
                mainProps.append(res)

            skill_weight = calc_file_dict["skill_weight"]
            jineng_index = skill_weight.index(max(skill_weight))
            jineng_name = [
                "普攻伤害加成",
                "重击伤害加成",
                "共鸣技能伤害加成",
                "共鸣解放伤害加成",
            ][jineng_index]

            subProps = i["subProps"]
            for sub_props_name in calc_file_dict["max_sub_props"]:
                _phantom_value = phantom_sub_value_map[sub_props_name][-1]
                if sub_props_name.startswith("技能"):
                    sub_props_name = jineng_name
                res = {
                    "attributeName": sub_props_name.replace("%", ""),
                    "attributeValue": _phantom_value,
                }
                subProps.append(res)

            list_index += 1

    return char_template_data


if __name__ == "__main__":
    read_calc_json_files(MAP_PATH)
