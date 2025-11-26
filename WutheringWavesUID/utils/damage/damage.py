from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Union

from ...utils.api.model import RoleDetailData
from ...utils.damage.utils import AbnormalType, parse_skill_multi
from .constants import onlineLevel2EquivalentLevel, spectro_frazzle_effect_atk


class WavesEffect(object):
    def __init__(self, element_msg: str, element_value: Any):
        self.element_msg = element_msg
        self.element_value = element_value

    def __str__(self):
        return f"msg={self.element_msg}, value={self.element_value})"

    @classmethod
    def add_effect(cls, title, msg):
        if not title or not msg:
            return
        e = WavesEffect(f"{title}", f"{msg}")
        return e


def calc_percent_expression(express) -> float:
    """
    计算包含百分比的数学表达式。

    :param express: 字符串形式的数学表达式，例如 "22.38%+13.06%*4"
    :return: 计算结果，浮点数
    """
    # 将百分号替换为小数表示
    express = express.replace("%", "/100")

    try:
        result = eval(express)
    except Exception as e:
        raise ValueError(f"无法计算表达式: {express}") from e

    return result


class PhantomDetail:
    def __init__(self, ph_name: str = "", ph_num: int = 0):
        self.ph_name = ph_name
        self.ph_num = ph_num

    def __str__(self):
        return f"(name={self.ph_name}, count={self.ph_num})"

    @classmethod
    def dict2Object(cls, d):
        res = PhantomDetail()
        res.ph_name = d.get("ph_name", "")
        res.ph_num = d.get("ph_num", 0)
        return res


@dataclass
class DamageBonusPhantom:
    attack_damage: float = 0  # 普攻伤害加成
    hit_damage: float = 0  # 重击伤害加成
    skill_damage: float = 0  # 共鸣技能伤害加成
    liberation_damage: float = 0  # 共鸣解放伤害加成
    phantom_damage: float = 0  # 声骸伤害加成
    heal_bonus: float = 0  # 治疗效果加成
    shuxing_bonus: float = 0  # 属性伤害加成

    def __str__(self):
        return (
            f"DamageBonusPhantom(\n"
            f"    attack_damage={self.attack_damage}, \n"
            f"    hit_damage={self.hit_damage}, \n"
            f"    skill_damage={self.skill_damage}, \n"
            f"    liberation_damage={self.liberation_damage}, \n"
            f"    phantom_damage={self.phantom_damage}, \n"
            f"    heal_bonus={self.heal_bonus}\n"
            f"    shuxing_bonus={self.shuxing_bonus}\n"
            f")"
        )

    @classmethod
    def dict2Object(cls, d):
        res = DamageBonusPhantom()
        res.attack_damage = d.get("attack_damage", 0)
        res.hit_damage = d.get("hit_damage", 0)
        res.skill_damage = d.get("skill_damage", 0)
        res.liberation_damage = d.get("liberation_damage", 0)
        res.phantom_damage = d.get("phantom_damage", 0)
        res.heal_bonus = d.get("heal_bonus", 0)
        res.shuxing_bonus = d.get("shuxing_bonus", 0)
        return res


class DamageAttribute:
    def __init__(
        self,
        role=None,
        char_template: Literal["temp_atk", "temp_life", "temp_def"] = "temp_atk",
        char_atk=0,
        char_life=0,
        char_def=0,
        weapon_atk=0,
        atk_percent=0,
        life_percent=0,
        def_percent=0,
        atk_flat=0,
        life_flat=0,
        def_flat=0,
        skill_multi=0,
        healing_skill_multi="0+0%",
        shield_skill_multi="0+0%",
        skill_ratio=0,
        skill_ratio_in_skill_description=0,
        dmg_bonus=0,
        dmg_deepen=0,
        easy_damage=0,
        crit_rate=0,
        crit_dmg=0,
        character_level=0,
        defense_reduction=0,
        enemy_resistance=0.1,
        dmg_bonus_phantom: Optional[DamageBonusPhantom] = None,
        ph_detail=None,
        echo_id=0,
        char_attr=None,
        sync_strike=False,
        energy_regen=0,
        char_damage=None,
        enemy_level=90,
        teammate_char_ids: Optional[List[int]] = None,
        env_spectro=False,
        online_level=1,
    ):
        """
        初始化 DamageAttribute 类的实例。

        :param char_template: 角色模版 ["temp_atk", "temp_life", "temp_def"]
        :param char_atk: 基础攻击力 (角色基础攻击力
        :param char_life: 基础生命值 (角色基础生命值
        :param char_def: 基础防御力 (角色基础防御力
        :param weapon_atk: 基础攻击力 (武器基础攻击力
        :param atk_percent: 攻击力加成百分比 (例如 0.5 表示 50%)
        :param life_percent: 生命值加成百分比 (例如 0.5 表示 50%)
        :param def_percent: 防御力加成百分比 (例如 0.5 表示 50%)
        :param atk_flat: 固定攻击数值加成 (声骸固定攻击)
        :param life_flat: 固定生命数值加成 (声骸固定生命)
        :param def_flat: 固定防御数值加成 (声骸固定防御)
        :param skill_multi: 技能倍率
        :param skill_ratio: 技能倍率加成 (如命座 椿2命 = 1.2）
        :param dmg_bonus: 伤害加成百分比(热熔伤害加成+技能伤害加成）
        :param dmg_deepen: 伤害加深百分比
        :param crit_rate: 暴击率 (例如 0.5 表示 50%)
        :param crit_dmg: 暴击伤害倍率 (例如 2.0 表示 200%)
        :param character_level: 角色等级
        :param defense_reduction: 减防百分比
        :param enemy_resistance: 敌人抗性百分比
        :param dmg_bonus_phantom: 伤害加成百分比 -> DamageBonusPhantom
        :param ph_detail: 声骸个数和名字 -> List[PhantomDetail]
        :param echo_id: 声骸技能id
        :param char_attr: 角色属性 ["冷凝", "衍射", "导电", "热熔", "气动", "湮灭"]
        :param sync_strike: 协同攻击
        """
        if teammate_char_ids is None:
            teammate_char_ids = []
        self.role: Optional[RoleDetailData] = role
        # 角色模版 ["temp_atk", "temp_life", "temp_def"]
        self.char_template: Literal["temp_atk", "temp_life", "temp_def"] = char_template
        # 角色基础攻击力
        self.char_atk = char_atk
        # 角色基础生命值
        self.char_life = char_life
        # 角色基础防御力
        self.char_def = char_def
        # 武器基础攻击力
        self.weapon_atk = weapon_atk
        # 攻击力加成百分比
        self.atk_percent = atk_percent
        # 生命加成百分比
        self.life_percent = life_percent
        # 防御力加成百分比
        self.def_percent = def_percent
        # 固定攻击数值加成
        self.atk_flat = atk_flat
        # 固定生命数值加成
        self.life_flat = life_flat
        # 固定攻击数值加成
        self.def_flat = def_flat
        # 技能倍率
        self.skill_multi = skill_multi
        # 奶量技能倍率
        self.healing_skill_multi = healing_skill_multi
        # 盾量技能倍率
        self.shield_skill_multi = shield_skill_multi
        # 技能倍率加成 (如命座 椿2命 = 1.2）
        self.skill_ratio = skill_ratio
        # 技能倍率加成（技能描述里
        self.skill_ratio_in_skill_description = skill_ratio_in_skill_description
        # 伤害加成百分比
        self.dmg_bonus = dmg_bonus
        # 伤害加深百分比
        self.dmg_deepen = dmg_deepen
        # 易伤百分比
        self.easy_damage = easy_damage
        # 暴击率
        self.crit_rate = crit_rate
        # 暴击伤害
        self.crit_dmg = crit_dmg
        # 角色等级
        self.character_level = character_level
        # 减防百分比
        self.defense_reduction = defense_reduction
        # 敌人抗性百分比
        self.enemy_resistance = 0
        # 伤害加成百分比 -> DamageBonusPhantom
        self.dmg_bonus_phantom: Optional[DamageBonusPhantom] = dmg_bonus_phantom
        # 声骸个数和名字 -> List[PhantomDetail]
        self.ph_detail: List[PhantomDetail] = []
        # 声骸技能id
        self.echo_id = echo_id
        # 角色属性 ["冷凝", "衍射", "导电", "热熔", "气动", "湮灭"]
        self.char_attr: Optional[
            Literal["冷凝", "衍射", "导电", "热熔", "气动", "湮灭"]
        ] = char_attr
        # 角色属性伤害  attack_damage,hit_damage,skill_damage,liberation_damage,heal_bonus
        self.char_damage = char_damage
        # 协同攻击
        self.sync_strike = sync_strike
        # 共鸣效率
        self.energy_regen = energy_regen
        # 效果
        self.effect = []
        # 敌人等级
        self.enemy_level = 0
        # 队友id
        self.teammate_char_ids = teammate_char_ids if teammate_char_ids else []
        # 光噪效应
        self.env_spectro = env_spectro
        # 光噪效应伤害加深
        self.env_spectro_deepen = False
        # 风蚀效应
        self.env_aero_erosion = False
        # 风蚀效应伤害加深
        self.env_aero_erosion_deepen = False
        # 虚湮效应
        self.env_havoc_bane = False
        # 触发护盾
        self.trigger_shield = False
        # 声骸结果
        self.ph_result = False
        # 联觉等级
        self.online_level = online_level
        # 异常类型
        self.abnormalType = None

        if enemy_resistance:
            self.add_enemy_resistance(
                enemy_resistance, "敌人抗性", f"{enemy_resistance:.0%}"
            )
        self.set_enemy_level(enemy_level)

    def __str__(self):
        ph_details_str = "\n".join(str(ph) for ph in self.ph_detail)
        effect_str = "\n" + "\n".join(str(e) for e in self.effect)
        return (
            f"\nDamageAttribute(\n"
            f"  角色模版={self.char_template}, \n"
            f"  角色基础攻击力={self.char_atk}, \n"
            f"  角色基础生命值={self.char_life}, \n"
            f"  角色基础防御力={self.char_def}, \n"
            f"  武器基础攻击力={self.weapon_atk}, \n"
            f"  有效攻击力={self.effect_attack}, \n"
            f"  有效生命值={self.effect_life}, \n"
            f"  有效防御力={self.effect_def}, \n"
            f"  攻击力加成百分比={self.atk_percent}, \n"
            f"  生命值加成百分比={self.life_percent}, \n"
            f"  防御力加成百分比={self.def_percent}, \n"
            f"  声骸固定攻击数值={self.atk_flat}, \n"
            f"  声骸固定生命数值={self.life_flat}, \n"
            f"  声骸固定防御数值={self.def_flat}, \n"
            f"  技能倍率={self.skill_multi}, \n"
            f"  技能倍率加成={self.skill_ratio}, \n"
            f"  奶量技能倍率={self.healing_skill_multi}, \n"
            f"  伤害加成百分比={self.dmg_bonus}, \n"
            f"  伤害加深百分比={self.dmg_deepen}, \n"
            f"  暴击率={self.crit_rate}, \n"
            f"  暴击伤害={self.crit_dmg}, \n"
            f"  角色等级={self.character_level}, \n"
            f"  敌人等级={self.enemy_level}, \n"
            f"  减防百分比={self.defense_reduction}, \n"
            f"  减防乘区={self.defense_ratio}, \n"
            f"  敌人抗性百分比={self.enemy_resistance}, \n"
            f"  声骸的加成百分比={self.dmg_bonus_phantom}, \n"
            f"  角色属性={self.char_attr}, \n"
            f"  角色属性伤害={self.char_damage}, \n"
            f"  协同攻击={self.sync_strike}, \n"
            f"  触发护盾={self.trigger_shield}, \n"
            f"  共鸣效率={self.energy_regen}, \n"
            f"  声骸={ph_details_str}, \n"
            f"  效果={effect_str}, \n"
            f"  队友={self.teammate_char_ids}, \n"
            f")"
        )

    def set_role(self, role: RoleDetailData):
        self.role = role
        return self

    def add_effect(self, title: str, msg: str):
        effect = WavesEffect.add_effect(title, msg)
        if effect is None:
            return
        self.effect.append(effect)

    def get_effect(self, title: str):
        for effect in self.effect:
            if effect.element_msg != title:
                continue
            return effect.element_value

    def set_enemy_level(self, enemy_level: int):
        self.enemy_level = enemy_level

        title = "敌人等级"
        msg = f"{enemy_level}级"
        for effect in self.effect:
            if effect.element_msg == title:
                effect.element_value = msg
                break
        else:
            self.add_effect(title, msg)

        return self

    def set_char_template(
        self, char_template: Literal["temp_atk", "temp_life", "temp_def"]
    ):
        self.char_template = char_template
        return self

    def set_char_attr(
        self, char_attr: Literal["冷凝", "衍射", "导电", "热熔", "气动", "湮灭"]
    ):
        self.char_attr = char_attr
        return self

    def set_char_atk(self, char_atk: float, title="", msg=""):
        """设置角色基础攻击力"""
        self.char_atk = char_atk
        self.add_effect(title, msg)
        return self

    def set_char_life(self, char_life: float, title="", msg=""):
        """设置角色基础生命值"""
        self.char_life = char_life
        self.add_effect(title, msg)
        return self

    def set_char_def(self, char_def: float, title="", msg=""):
        """设置角色基础防御力"""
        self.char_def = char_def
        self.add_effect(title, msg)
        return self

    def set_weapon_atk(self, weapon_atk: float, title="", msg=""):
        """设置武器基础攻击力"""
        self.weapon_atk = weapon_atk
        self.add_effect(title, msg)
        return self

    def add_atk_percent(self, atk_percent: float, title="", msg=""):
        """增加攻击力百分比"""
        self.atk_percent += atk_percent
        self.add_effect(title, msg)
        return self

    def add_life_percent(self, life_percent: float, title="", msg=""):
        """增加生命百分比"""
        self.life_percent += life_percent
        self.add_effect(title, msg)
        return self

    def add_def_percent(self, def_percent: float, title="", msg=""):
        """增加防御力百分比"""
        self.def_percent += def_percent
        self.add_effect(title, msg)
        return self

    def set_atk_flat(self, atk_flat: float, title="", msg=""):
        """设置固定攻击数值"""
        self.atk_flat = atk_flat
        self.add_effect(title, msg)
        return self

    def add_atk_flat(self, atk_flat: float, title="", msg=""):
        """增加攻击数值 如洛可可大招"""
        self.atk_flat += atk_flat
        self.add_effect(title, msg)
        return self

    def set_life_flat(self, life_flat: float, title="", msg=""):
        """设置固定生命数值"""
        self.life_flat = life_flat
        self.add_effect(title, msg)
        return self

    def set_def_flat(self, def_flat: float, title="", msg=""):
        """设置固定防御数值"""
        self.def_flat = def_flat
        self.add_effect(title, msg)
        return self

    def add_skill_multi(self, skill_multi: Union[str, float], title="", msg=""):
        """增加技能倍率"""
        if isinstance(skill_multi, str):
            skill_multi = calc_percent_expression(skill_multi)
        self.skill_multi += skill_multi
        self.add_effect(title, msg)
        return self

    def set_skill_multi(self, skill_multi: Union[str, float], title="", msg=""):
        """设置技能倍率"""
        if isinstance(skill_multi, str):
            skill_multi = calc_percent_expression(skill_multi)
        self.skill_multi = skill_multi
        self.add_effect(title, msg)
        return self

    def add_healing_skill_multi(
        self, healing_skill_multi: Union[str, float], title="", msg=""
    ):
        """增加奶的技能倍率"""
        value1, percent1 = parse_skill_multi(self.healing_skill_multi)
        value2, percent2 = parse_skill_multi(healing_skill_multi)

        # 计算总和
        total_value = value1 + value2
        total_percent = percent1 + percent2

        self.healing_skill_multi = f"{total_value}+{total_percent}%"
        self.add_effect(title, msg)
        return self

    def add_shield_skill_multi(
        self, shield_skill_multi: Union[str, float], title="", msg=""
    ):
        """增加盾量的技能倍率"""

        value1, percent1 = parse_skill_multi(self.shield_skill_multi)
        value2, percent2 = parse_skill_multi(shield_skill_multi)

        # 计算总和
        total_value = value1 + value2
        total_percent = percent1 + percent2

        self.shield_skill_multi = f"{total_value}+{total_percent}%"
        self.add_effect(title, msg)
        return self

    def add_skill_ratio(self, skill_ratio: Union[str, float], title="", msg=""):
        """增加技能倍率加成 -> 技能伤害倍率提升"""
        if isinstance(skill_ratio, str):
            skill_ratio = calc_percent_expression(skill_ratio)
        self.skill_ratio += skill_ratio
        self.add_effect(title, msg)
        return self

    def add_skill_ratio_in_skill_description(
        self, skill_ratio: Union[str, float], title="", msg=""
    ):
        """增加技能倍率加成 -> 技能伤害倍率提升"""
        if isinstance(skill_ratio, str):
            skill_ratio = calc_percent_expression(skill_ratio)
        self.skill_ratio_in_skill_description += skill_ratio
        self.add_effect(title, msg)
        return self

    def add_dmg_bonus(self, dmg_bonus: float, title="", msg=""):
        """增加伤害加成百分比"""
        self.dmg_bonus += dmg_bonus
        self.add_effect(title, msg)
        return self

    def add_dmg_deepen(self, dmg_deepen: float, title="", msg=""):
        """增加伤害加深百分比"""
        self.dmg_deepen += dmg_deepen
        self.add_effect(title, msg)
        return self

    def add_easy_damage(self, easy_damage: float, title="", msg=""):
        """增加易伤百分比"""
        self.easy_damage += easy_damage
        self.add_effect(title, msg)
        return self

    def add_crit_rate(self, crit_rate: float, title="", msg=""):
        """设置暴击率"""
        self.crit_rate += crit_rate
        self.add_effect(title, msg)
        return self

    def add_crit_dmg(self, crit_dmg: float, title="", msg=""):
        """设置暴击伤害倍率"""
        self.crit_dmg += crit_dmg
        self.add_effect(title, msg)
        return self

    def set_character_level(self, character_level: int, title="", msg=""):
        """设置角色等级"""
        self.character_level = character_level
        self.add_effect(title, msg)
        return self

    def add_defense_reduction(self, defense_reduction: float, title="", msg=""):
        """增加减防百分比"""
        self.defense_reduction += defense_reduction
        self.add_effect(title, msg)
        return self

    def add_enemy_resistance(self, enemy_resistance: float, title="", msg=""):
        """增加敌人抗性百分比"""
        self.enemy_resistance += enemy_resistance
        self.add_effect(title, msg)
        return self

    def add_energy_regen(self, energy_regen: float):
        """增加共鸣效率"""
        self.energy_regen += energy_regen

    def set_dmg_bonus_phantom(self, dmg_bonus_phantom_map: Dict):
        """设置声骸加成"""
        if dmg_bonus_phantom_map:
            dmg_bonus_phantom = DamageBonusPhantom.dict2Object(dmg_bonus_phantom_map)
        else:
            dmg_bonus_phantom = DamageBonusPhantom()
        self.dmg_bonus_phantom = dmg_bonus_phantom
        return self

    def add_ph_detail(self, ph_detail: Dict):
        if not ph_detail:
            return self
        self.ph_detail.append(PhantomDetail.dict2Object(ph_detail))
        return self

    def set_ph_result(self, ph_result: bool):
        """设置声骸结果"""
        self.ph_result = ph_result
        return self

    def set_echo_id(self, echo_id: int):
        """声骸技能的id"""
        self.echo_id = echo_id
        return self

    def set_sync_strike(self):
        """协同攻击"""
        self.sync_strike = True
        return self

    def is_env_abnormal(self):
        """是否有异常效果"""
        return any(
            [
                self.env_spectro,
                self.env_aero_erosion,
                self.env_havoc_bane,
            ]
        )

    def set_env_spectro(self):
        """光噪效应"""
        self.env_spectro = True
        return self

    def set_env_spectro_deepen(self):
        """光噪效应伤害加深"""
        self.env_spectro_deepen = True
        return self

    def set_env_aero_erosion(self):
        """风蚀效应"""
        self.env_aero_erosion = True
        return self

    def set_env_aero_erosion_deepen(self):
        """风蚀效应伤害加深"""
        self.env_aero_erosion_deepen = True
        return self

    def set_env_havoc_bane(self):
        """虚湮效应"""
        self.env_havoc_bane = True
        return self

    def set_trigger_shield(self):
        """触发护盾"""
        self.trigger_shield = True
        return self

    def set_char_damage(self, char_damage):
        """角色伤害"""
        self.char_damage = char_damage
        return self

    def add_teammate(self, teammate_char_ids: Union[List[int], int, None]):
        """队友"""
        if teammate_char_ids is None:
            return self
        if isinstance(teammate_char_ids, int):
            teammate_char_ids = [teammate_char_ids]
        self.teammate_char_ids.extend(teammate_char_ids)
        return self

    def set_phantom_dmg_bonus(self, needPhantom=True, needShuxing=True):
        if not self.dmg_bonus_phantom:
            return self
        if needPhantom:
            if self.char_damage:
                value = getattr(self.dmg_bonus_phantom, self.char_damage)
                self.add_dmg_bonus(value)
        if needShuxing:
            value = self.dmg_bonus_phantom.shuxing_bonus
            self.add_dmg_bonus(value)
        return self

    @property
    def base_atk(self):
        """基础攻击力"""
        return self.char_atk + self.weapon_atk

    @property
    def effect_attack(self):
        """
        计算有效攻击力。

        :return: 有效攻击力
        """
        return self.base_atk * (1 + self.atk_percent) + self.atk_flat

    @property
    def effect_life(self):
        """
        计算有效生命。

        :return: 计算有效生命
        """
        return self.char_life * (1 + self.life_percent) + self.life_flat

    @property
    def effect_def(self):
        """
        计算有效防御。

        :return: 计算有效防御
        """
        return self.char_def * (1 + self.def_percent) + self.def_flat

    @property
    def defense_ratio(self):
        """
        计算敌人的防御减伤比。

        :return: 防御减伤比
        """
        # enemy_defense = 1512
        enemy_defense = self.enemy_level * 8 + 792
        # 计算公式为 (800 + 8 * 等级) / (800 + 8 * 等级 + 敌人防御 * (1 - 减防))
        return (800 + 8 * self.character_level) / (
            800
            + 8 * self.character_level
            + enemy_defense * (1 - self.defense_reduction)
        )

    @property
    def valid_enemy_resistance(self):
        """
        计算敌人抗性减伤比。

        :return: 敌人抗性减伤比
        """
        if self.enemy_resistance < 0:
            return 1 - self.enemy_resistance / 2
        elif self.enemy_resistance >= 0.8:
            return 0.2 / (0.2 + self.enemy_resistance)
        else:
            return 1 - self.enemy_resistance

    def calculate_crit_damage(self, effect_value=None):
        """
        计算暴击伤害。

        :return: 暴击伤害值
        """
        if not effect_value:
            effect_value = self.effect_attack
        # 计算暴击伤害
        return (
            effect_value
            * self.skill_multi
            * (1 + self.skill_ratio)
            * (1 + self.skill_ratio_in_skill_description)
            * (1 + self.dmg_bonus)
            * (1 + self.dmg_deepen)
            * (1 + self.easy_damage)
            * self.valid_enemy_resistance
            * self.defense_ratio
            * self.crit_dmg
        )

    def calculate_expected_damage(self, effect_value=None):
        """
        计算期望伤害。

        :return: 期望伤害值
        """
        if self.crit_rate > 1:
            return self.calculate_crit_damage(effect_value)

        if not effect_value:
            effect_value = self.effect_attack

        return (
            effect_value
            * self.skill_multi
            * (1 + self.skill_ratio)
            * (1 + self.skill_ratio_in_skill_description)
            * (1 + self.dmg_bonus)
            * (1 + self.dmg_deepen)
            * (1 + self.easy_damage)
            * self.valid_enemy_resistance
            * self.defense_ratio
            * (self.crit_rate * (self.crit_dmg - 1) + 1)
        )

    def calculate_healing(self, effect_value):
        """
        计算治疗量。
        """
        flat, percent = parse_skill_multi(self.healing_skill_multi)
        return effect_value * (percent * 0.01) * (1 + self.dmg_bonus) + flat * (
            1 + self.dmg_bonus
        )

    def calculate_shield(self, effect_value):
        """
        计算盾量。
        """
        flat, percent = parse_skill_multi(self.shield_skill_multi)
        return effect_value * (percent * 0.01) * (1 + self.dmg_bonus) + flat * (
            1 + self.dmg_bonus
        )


class AbnormalSpectroFrazzle:
    """光噪效应"""

    typeId: AbnormalType = "SpectroFrazzle"

    # 基础区
    # 光噪层数区（技能倍率区）
    # 防御区
    # 抗性区 同基础 self.attr.valid_enemy_resistance
    # 伤害减免区
    # 光噪伤害加深区

    # 光噪伤害 = 基础区 * 光噪层数区 * 防御区 * 抗性区 * 伤害减免区 * 光噪伤害加深区

    def __init__(
        self,
        attr: DamageAttribute,
        floor: int = 0,
        env: Literal["大世界", "副本"] = "大世界",
        dmg_deepen: float = 0,
        dmg_reduce: float = 0,
        dmg_increase: float = 0,
    ):
        self.attr = attr
        self.floor = floor
        self.env = env
        self.dmg_deepen = dmg_deepen
        # 受到伤害减少
        self.dmg_reduce = dmg_reduce
        # 收到伤害增加
        self.dmg_increase = dmg_increase

        self.online_level = self.attr.online_level
        self.attr.add_effect("光噪效应环境", f"{env}")
        self.attr.add_effect("联觉等级", f"{self.online_level}")

    def add_floor(self, floor: int, title="", msg=""):
        """增加光噪层数"""
        self.floor += floor
        self.attr.add_effect(title, msg)
        return self

    def add_dmg_deepen(self, dmg_deepen: float, title="", msg=""):
        """增加光噪伤害加深"""
        self.dmg_deepen += dmg_deepen
        self.attr.add_effect(title, msg)
        return self

    def add_dmg_reduce(self, dmg_reduce: float, title="", msg=""):
        """增加光噪伤害减免"""
        self.dmg_reduce += dmg_reduce
        self.attr.add_effect(title, msg)
        return self

    def add_dmg_increase(self, dmg_increase: float, title="", msg=""):
        """增加光噪伤害增加"""
        self.dmg_increase += dmg_increase
        self.attr.add_effect(title, msg)
        return self

    @property
    def defense_ratio(self):
        """
        计算敌人的防御减伤比。

        :return: 防御减伤比
        """
        if self.env == "大世界":
            level = onlineLevel2EquivalentLevel[self.online_level - 1]
            # 计算公式为 (等级 + 100) / (等级 + 怪物等级 + 199)
            return (level + 100) / (level + self.attr.enemy_level + 199)
        else:
            # 计算公式为 (怪物等级 + 100) / (怪物等级*2 + 199)
            return (self.attr.enemy_level + 100) / (self.attr.enemy_level * 2 + 199)

    @property
    def valid_dmg_reduce(self):
        """
        计算有效伤害减免。

        :return: 有效伤害减免
        """
        return 1 - (self.dmg_reduce + self.dmg_increase)

    @property
    def valid_floor(self):
        """
        计算有效光噪层数。
        0.2439*层数（技能等级）+0.561

        :return: 有效光噪层数
        """
        if self.floor > 10 or self.floor <= 0:
            floor = 10
        else:
            floor = self.floor
        return 0.2439 * floor + 0.561

    @property
    def base_damage(self):
        """
        计算基础伤害。

        :return: 基础伤害值
        """
        if self.attr.role:
            char_level = self.attr.role.level
        else:
            char_level = 90
        return spectro_frazzle_effect_atk[char_level - 1]

    def calculate_damage(self):
        """
        计算伤害。

        :return: 伤害值
        """
        return (
            self.base_damage
            * self.valid_floor
            * self.defense_ratio
            * self.attr.valid_enemy_resistance
            * self.valid_dmg_reduce
            * (1 + self.dmg_deepen)
        )


def check_char_id(attr: DamageAttribute, char_id: Union[int, List[int]]):
    if isinstance(char_id, int):
        return attr.role and attr.role.role.roleId == char_id
    else:
        return attr.role and attr.role.role.roleId in char_id
