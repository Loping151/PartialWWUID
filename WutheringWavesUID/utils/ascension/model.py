from typing import Any, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field

from ...utils.resource.constant import ATTRIBUTE_ID_MAP
from ...utils.util import format_with_defaults


class Stats(BaseModel):
    life: float
    atk: float
    def_: float = Field(..., alias="def")  # `def` is a reserved keyword, use `def_`


class WeaponStats(BaseModel):
    name: str
    value: Union[str, float]
    isRatio: bool
    isPercent: bool


class LevelExp(BaseModel):
    level: int
    exp: int


class SkillLevel(BaseModel):
    name: str
    param: List[List[str]]


class Skill(BaseModel):
    name: str
    desc: str
    param: List[str]
    type: Optional[str] = None
    level: Optional[Dict[str, SkillLevel]] = None

    def get_desc_detail(self):
        return format_with_defaults(self.desc, self.param)


class Chain(BaseModel):
    name: str
    desc: str
    param: List[Union[str, float]]

    def get_desc_detail(self):
        return format_with_defaults(self.desc, self.param)


class AscensionMaterial(BaseModel):
    key: int
    value: int


class CharacterModel(BaseModel):
    name: str
    starLevel: int
    attributeId: int
    weaponTypeId: int
    stats: Dict[str, Dict[str, Stats]]
    skillTree: Dict[str, Dict[str, Skill]]
    chains: Dict[int, Chain]
    ascensions: Dict[str, List[AscensionMaterial]]

    class Config:
        # Updated configuration keys for Pydantic v2
        populate_by_name = True  # Replaces `allow_population_by_field_name`
        str_strip_whitespace = True  # Replaces `anystr_strip_whitespace`
        str_min_length = 1  # Replaces `min_anystr_length`

    def get_max_level_stat(self) -> Stats:
        return self.stats["6"]["90"]

    def get_attribute_name(self) -> str:
        return ATTRIBUTE_ID_MAP[self.attributeId]


class WeaponModel(BaseModel):
    name: str
    type: int
    starLevel: int
    stats: Dict[str, Dict[str, List[WeaponStats]]]
    effect: str
    effectName: str
    param: List[List[str]]
    desc: str
    ascensions: Dict[str, List[AscensionMaterial]]

    class Config:
        # Updated configuration keys for Pydantic v2
        populate_by_name = True  # Replaces `allow_population_by_field_name`
        str_strip_whitespace = True  # Replaces `anystr_strip_whitespace`
        str_min_length = 1  # Replaces `min_anystr_length`

    def get_max_level_stat_tuple(self) -> List[Tuple[str, str]]:
        stats = self.stats["6"]["90"]
        rets = []
        for stat in stats:
            if stat.isPercent:
                ret = f"{float(stat.value) / 100:.1f}%"
            elif stat.isRatio:
                ret = f"{stat.value * 100:.1f}%"
            else:
                ret = f"{int(stat.value)}"
            rets.append((stat.name, ret))

        return rets

    def get_effect_detail(self):
        return self.effect.format(
            *["(" + "/".join(i) + ")" if len(set(i)) > 1 else i[0] for i in self.param]
        )

    def get_ascensions_max_list(self):
        for i in ["5", "4", "3", "2"]:
            try:
                value = [j.key for j in self.ascensions[i]]
                return value
            except Exception:
                continue
        return []

    def get_weapon_type(self) -> str:
        weapon_type = {
            1: "长刃",
            2: "迅刀",
            3: "佩枪",
            4: "臂铠",
            5: "音感仪",
        }
        return weapon_type.get(self.type, "")


"""
{
  "id": 6000039,
  "name": "朔雷之鳞",
  "intensityCode": 2,
  "group": {
    "3": {
      "name": "彻空冥雷"
    }
  },
  "skill": {
    "desc": "使用声骸技能，幻形为朔雷之鳞，可连续使用最多2次，甩尾召唤出来的雷击每段造成{0}的导电伤害，爪击造成{1}的导电伤害。\n爪击命中后，自身导电伤害加成提升{2}，重击伤害加成提升{3}，持续{4}秒。\n技能冷却：{5}秒",
    "simpleDesc": "幻形为朔雷之鳞，连续攻击敌人造成导电伤害，提高自身的导电和重击伤害。",
    "params": [
      [
        "64.05%",
        "109.80%",
        "12.00%",
        "12.00%",
        "15",
        "20"
      ],
      [
        "73.66%",
        "126.27%",
        "12.00%",
        "12.00%",
        "15",
        "20"
      ],
      [
        "83.27%",
        "142.74%",
        "12.00%",
        "12.00%",
        "15",
        "20"
      ],
      [
        "92.87%",
        "159.21%",
        "12.00%",
        "12.00%",
        "15",
        "20"
      ],
      [
        "102.48%",
        "175.68%",
        "12.00%",
        "12.00%",
        "15",
        "20"
      ]
    ]
  }
}
"""


class EchoModel(BaseModel):
    id: int
    name: str
    intensityCode: int
    group: Dict[str, Dict[str, str]]
    skill: Dict[str, Any]

    class Config:
        populate_by_name = True
        str_strip_whitespace = True
        str_min_length = 1

    def get_skill_detail(self):
        return format_with_defaults(self.skill["desc"], self.skill["params"][-1])

    def get_intensity(self) -> List[Tuple[str, str]]:
        temp_cost = {0: "c1", 1: "c3", 2: "c4", 3: "c4"}
        temp_level = {0: "轻波级", 1: "巨浪级", 2: "怒涛级", 3: "海啸级"}
        result = []
        result.append(("声骸等级", temp_level[self.intensityCode]))
        result.append(("「COST」", temp_cost[self.intensityCode]))
        return result

    def get_group_name(self) -> List[str]:
        return [i["name"] for i in self.group.values()]
