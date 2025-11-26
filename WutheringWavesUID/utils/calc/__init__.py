import copy
from typing import Any, Dict, List, Optional, Union

from gsuid_core.logger import logger

from ...utils.api.model import Props, RoleDetailData
from ...utils.api.model_other import EnemyDetailData
from ...utils.damage.utils import (
    SONATA_ANCIENT,
    SONATA_TIDEBREAKING,
    Ancient_Role_Ids,
)
from ...utils.map.damage.damage import check_if_ph_3, check_if_ph_5
from ..ascension.char import WavesCharResult, get_char_detail
from ..ascension.constant import percent_to_float, sum_numbers, sum_percentages
from ..ascension.sonata import WavesSonataResult, get_sonata_detail
from ..ascension.weapon import WavesWeaponResult, get_weapon_detail
from ..damage.abstract import WavesEchoRegister
from ..damage.damage import DamageAttribute
from ..resource.constant import card_sort_map as card_sort_map_back


class WuWaCalc(object):
    def __init__(
        self,
        role_detail: RoleDetailData,
        enemy_detail: Optional[EnemyDetailData] = None,
    ):
        """
        # 声骸预处理 -> 声骸套装，声骸数量，声骸首位id
        self.phantom_pre = self.prepare_phantom()

        # 声骸面板数据
        self.phantom_card = self.enhance_summation_phantom_value(self.phantom_pre)

        # 角色评分使用
        self.calc_temp = get_calc_map(self.phantom_card, role_detail.role.roleName)

        # 角色面板数据
        self.role_card = self.enhance_summation_card_value(self.phantom_card)

        # attr
        self.damageAttribute = self.card_sort_map_to_attribute(self.role_card)


        calc: WuWaCalc = WuWaCalc(role_detail)
        calc.phantom_pre = calc.prepare_phantom()
        calc.phantom_card = calc.enhance_summation_phantom_value(calc.phantom_pre)
        calc.calc_temp = get_calc_map(calc.phantom_card, role_detail.role.roleName)
        calc.role_card = calc.enhance_summation_card_value(calc.phantom_card)
        calc.damageAttribute = calc.card_sort_map_to_attribute(calc.role_card)
        """
        self.role_detail: RoleDetailData = role_detail
        # 声骸预处理 -> 声骸套装，声骸数量，声骸首位id
        self.phantom_pre = {}
        # 声骸面板数据
        self.phantom_card = {}
        # 角色评分使用
        self.calc_temp = None
        # 角色面板数据
        self.role_card = {}
        # attr
        self.damageAttribute: Optional[DamageAttribute] = None
        # 敌人
        if not enemy_detail:
            self.enemy_detail = EnemyDetailData()
        else:
            self.enemy_detail = enemy_detail
        self.can_calc = False
        if (
            self.role_detail.phantomData
            and self.role_detail.phantomData.equipPhantomList
        ):
            self.can_calc = False
            return
        self.can_calc = True

    def sum_phantom_value(self, result: Dict[str, str], prop_list: List[Props]) -> Dict:
        name_per = ["攻击", "生命", "防御"]

        for prop in prop_list:
            per = "%" in prop.attributeValue
            name = prop.attributeName
            if per and name in name_per:
                name = f"{name}%"
            if name not in result:
                result[name] = prop.attributeValue
                continue

            if per:
                old = float(result[name].replace("%", ""))
                new = float(prop.attributeValue.replace("%", ""))
                result[name] = f"{old + new:.1f}%"
            else:
                old = int(result[name])
                new = int(prop.attributeValue)
                result[name] = f"{old + new:d}"

        return result

    def prepare_phantom(self):
        result = {"ph_detail": [], "echo_id": 0}
        if not self.role_detail.phantomData:
            return result
        equipPhantomList = self.role_detail.phantomData.equipPhantomList
        if not equipPhantomList:
            return result
        temp_result = {}
        for i, _phantom in enumerate(equipPhantomList):
            if _phantom and _phantom.phantomProp:
                if i == 0:
                    result["echo_id"] = _phantom.phantomProp.phantomId
                props = _phantom.get_props()
                result = self.sum_phantom_value(result, props)
                sonata_result: WavesSonataResult = get_sonata_detail(
                    _phantom.fetterDetail.name
                )
                if sonata_result.name not in temp_result:
                    temp_result[sonata_result.name] = {
                        "phantomIds": [_phantom.phantomProp.phantomId],
                        "result": sonata_result,
                    }
                else:
                    temp_result[sonata_result.name]["phantomIds"].append(
                        _phantom.phantomProp.phantomId
                    )

        for key, value in temp_result.items():
            num = len(value["phantomIds"])
            waves_sonata_result: WavesSonataResult = value["result"]
            two_piece = waves_sonata_result.piece(2)
            # 2件套效果，声骸数量大于等于2
            if two_piece and num >= 2:
                name: str | Any = two_piece.effect
                effect = two_piece.param[0]
                result["ph"] = waves_sonata_result.name
                if name not in result:
                    result[name] = effect
                else:
                    old = float(result[name].replace("%", ""))
                    new = float(effect.replace("%", ""))
                    result[name] = f"{old + new:.1f}%"

            result["ph_detail"].append(
                {
                    "ph_num": num,
                    "ph_name": key,
                    "isFull": num == waves_sonata_result.full_piece_effect(),
                }
            )

        return result

    def enhance_summation_phantom_value(
        self,
        result: Dict[str, Union[str, float]],
    ):
        role_id = self.role_detail.role.roleId
        role_level = self.role_detail.role.level
        role_breach = self.role_detail.role.breach
        weaponData = self.role_detail.weaponData
        weapon_id = weaponData.weapon.weaponId
        weapon_level = weaponData.level
        weapon_breach = weaponData.breach
        weapon_reson_level = weaponData.resonLevel

        char_result: WavesCharResult = get_char_detail(
            role_id,
            role_level,
            role_breach,
        )

        weapon_result: WavesWeaponResult = get_weapon_detail(
            weapon_id,
            weapon_level,
            weapon_breach,
            weapon_reson_level,
        )

        # 基础生命
        _life = char_result.stats["life"]
        # 基础攻击
        _atk = char_result.stats["atk"]
        # 基础防御
        _def = char_result.stats["def"]

        # 武器基础攻击
        _weapon_atk = weapon_result.stats[0]["value"]
        result["atk_flat"] = float(result.get("攻击", "0"))
        result["life_flat"] = float(result.get("生命", "0"))
        result["def_flat"] = float(result.get("防御", "0"))

        base_atk = float(_atk) + float(_weapon_atk)
        per_atk = percent_to_float(result.get("攻击%", "0%"))
        result["atk_percent"] = per_atk
        new_atk = int(base_atk * per_atk) + int(result.get("攻击", "0"))
        result["攻击"] = f"{new_atk}"

        base_life = float(_life)
        per_life = percent_to_float(result.get("生命%", "0%"))
        result["life_percent"] = per_life
        new_life = int(base_life * per_life) + int(result.get("生命", "0"))
        result["生命"] = f"{new_life}"

        base_def = float(_def)
        per_def = percent_to_float(result.get("防御%", "0%"))
        result["def_percent"] = per_def
        new_def = int(base_def * per_def) + int(result.get("防御", "0"))
        result["防御"] = f"{new_def}"

        # 声骸首位
        if "echo_id" in result:
            echo_clz = WavesEchoRegister.find_class(result["echo_id"])
            if echo_clz:
                e = echo_clz()
                temp = e.do_equipment_first(role_id)
                logger.debug(f"首位声骸数据 {e.name}-{e.id}-{temp}")
                for key, value in temp.items():
                    if key not in result:
                        result[key] = value
                    else:
                        _value = result[key]
                        if isinstance(_value, str):
                            old = float(_value.replace("%", ""))
                            new = float(value.replace("%", ""))
                            result[key] = f"{old + new:.1f}%"

        return result

    def enhance_summation_card_value(
        self,
        result,
    ):
        role_id = self.role_detail.role.roleId
        role_level = self.role_detail.role.level
        role_breach = self.role_detail.role.breach
        role_attr = self.role_detail.role.attributeName
        weaponData = self.role_detail.weaponData
        weapon_id = weaponData.weapon.weaponId
        weapon_level = weaponData.level
        weapon_breach = weaponData.breach
        weapon_reson_level = weaponData.resonLevel

        shuxing = f"{role_attr}伤害加成"
        card_sort_map: Dict[str, Any] = copy.deepcopy(card_sort_map_back)
        char_result: WavesCharResult = get_char_detail(role_id, role_level, role_breach)
        weapon_result: WavesWeaponResult = get_weapon_detail(
            weapon_id, weapon_level, weapon_breach, weapon_reson_level
        )

        # 基础生命
        _life = char_result.stats["life"]
        # 基础攻击
        _atk = char_result.stats["atk"]
        # 基础防御
        _def = char_result.stats["def"]
        # 武器基础攻击
        _weapon_atk = weapon_result.stats[0]["value"]
        card_sort_map["char_atk"] = float(_atk)
        card_sort_map["weapon_atk"] = float(_weapon_atk)
        card_sort_map["char_life"] = float(_life)
        card_sort_map["char_def"] = float(_def)
        # 武器副词条
        weapon_sub_name = weapon_result.stats[1]["name"]
        weapon_sub_value = weapon_result.stats[1]["value"]
        card_sort_map[weapon_sub_name] = sum_percentages(
            weapon_sub_value, card_sort_map[weapon_sub_name]
        )

        # 武器谐振
        if weapon_result.sub_effect:
            # sub_name = ["生命提升", "共鸣效率提升", "攻击提升", "全属性伤害加成提升"]
            sub_effect_name = weapon_result.sub_effect["name"]
            card_sort_map[sub_effect_name] = sum_percentages(
                weapon_result.sub_effect["value"], card_sort_map[sub_effect_name]
            )

        # 角色固有技能
        for name, value in char_result.fixed_skill.items():
            if name not in card_sort_map:
                card_sort_map[name] = "0%"
            card_sort_map[name] = sum_percentages(value, card_sort_map[name])

        char_regen = "100%"
        card_sort_map["共鸣效率"] = sum_percentages(
            char_regen, result.get("共鸣效率", "0%"), card_sort_map["共鸣效率"]
        )
        card_sort_map["energy_regen"] = percent_to_float(card_sort_map["共鸣效率"])

        card_sort_map["ph_detail"] = result.get("ph_detail", [])

        card_sort_map["ph_result"] = False
        for ph_detail in card_sort_map.get("ph_detail", []):
            if not ph_detail:
                continue
            # 无惧浪涛之勇
            if check_if_ph_5(
                ph_detail["ph_name"], ph_detail["ph_num"], SONATA_TIDEBREAKING
            ):
                # 角色攻击提升15%，共鸣效率达到250%后，当前角色全属性伤害提升30%
                result["atk_percent"] += 0.15
                if card_sort_map["energy_regen"] >= 2.5:
                    card_sort_map["属性伤害加成"] = sum_percentages(
                        "30%",
                        card_sort_map["属性伤害加成"],
                    )
                card_sort_map["ph_result"] = True

            # 失序彼岸之梦
            if role_id in Ancient_Role_Ids and check_if_ph_3(
                ph_detail["ph_name"], ph_detail["ph_num"], SONATA_ANCIENT
            ):
                # 角色共鸣能量为0时，暴击率提升35%
                card_sort_map["暴击"] = sum_percentages(
                    "20%",
                    card_sort_map["暴击"],
                )
                card_sort_map["ph_result"] = True

        base_atk = float(sum_numbers(_atk, _weapon_atk))
        # 各种攻击百分比 = 武器副词条+武器谐振+固有技能
        per_temp = percent_to_float(card_sort_map["攻击"])
        card_sort_map["atk_percent"] = per_temp + result.get("atk_percent", 0)
        card_sort_map["atk_flat"] = float(result.get("atk_flat", 0))
        card_sort_map["攻击"] = sum_numbers(
            base_atk, result.get("攻击", 0), round(base_atk * per_temp)
        )
        card_sort_map["攻击"] = f"{card_sort_map['攻击'].split('.')[0]}"

        base_life = float(_life)
        per_life = percent_to_float(card_sort_map["生命"])
        card_sort_map["life_percent"] = per_life + result.get("life_percent", 0)
        card_sort_map["life_flat"] = float(result.get("life_flat", 0))
        card_sort_map["生命"] = sum_numbers(
            _life, result.get("生命", 0), round(base_life * per_life)
        )
        card_sort_map["生命"] = f"{card_sort_map['生命'].split('.')[0]}"

        base_def = float(_def)
        per_def = percent_to_float(card_sort_map["防御"])
        card_sort_map["def_percent"] = per_def + result.get("def_percent", 0)
        card_sort_map["def_flat"] = float(result.get("def_flat", 0))
        card_sort_map["防御"] = sum_numbers(
            _def, result.get("防御", 0), round(base_def * per_def)
        )
        card_sort_map["防御"] = f"{card_sort_map['防御'].split('.')[0]}"

        # 固定暴击
        char_crit_rate = "5%"
        # 固定爆伤
        char_crit_dmg = "150%"

        card_sort_map["暴击"] = sum_percentages(
            char_crit_rate, result.get("暴击", "0%"), card_sort_map["暴击"]
        )
        card_sort_map["crit_rate"] = percent_to_float(card_sort_map["暴击"])
        card_sort_map["暴击伤害"] = sum_percentages(
            char_crit_dmg, result.get("暴击伤害", "0%"), card_sort_map["暴击伤害"]
        )
        card_sort_map["crit_dmg"] = percent_to_float(card_sort_map["暴击伤害"])

        card_sort_map[shuxing] = sum_percentages(
            result.get(shuxing, "0%"),
            card_sort_map.get(shuxing, "0%"),
            card_sort_map.get("属性伤害加成", "0%"),
        )
        card_sort_map["shuxing_bonus"] = percent_to_float(card_sort_map[shuxing])
        card_sort_map["char_attr"] = role_attr

        if "属性伤害加成" in card_sort_map:
            del card_sort_map["属性伤害加成"]

        card_sort_map["普攻伤害加成"] = sum_percentages(
            result.get("普攻伤害加成", "0%"), card_sort_map.get("普攻伤害加成", "0%")
        )
        card_sort_map["attack_damage"] = percent_to_float(card_sort_map["普攻伤害加成"])

        card_sort_map["重击伤害加成"] = sum_percentages(
            result.get("重击伤害加成", "0%"), card_sort_map.get("重击伤害加成", "0%")
        )
        card_sort_map["hit_damage"] = percent_to_float(card_sort_map["重击伤害加成"])

        card_sort_map["共鸣技能伤害加成"] = sum_percentages(
            result.get("共鸣技能伤害加成", "0%"),
            card_sort_map.get("共鸣技能伤害加成", "0%"),
        )
        card_sort_map["skill_damage"] = percent_to_float(
            card_sort_map["共鸣技能伤害加成"]
        )

        card_sort_map["共鸣解放伤害加成"] = sum_percentages(
            result.get("共鸣解放伤害加成", "0%"),
            card_sort_map.get("共鸣解放伤害加成", "0%"),
        )
        card_sort_map["liberation_damage"] = percent_to_float(
            card_sort_map["共鸣解放伤害加成"]
        )

        card_sort_map["声骸技能伤害加成"] = sum_percentages(
            result.get("声骸技能伤害加成", "0%"),
            card_sort_map.get("声骸技能伤害加成", "0%"),
        )
        card_sort_map["phantom_damage"] = percent_to_float(
            card_sort_map["声骸技能伤害加成"]
        )

        card_sort_map["治疗效果加成"] = sum_percentages(
            result.get("治疗效果加成", "0%"), card_sort_map.get("治疗效果加成", "0%")
        )
        card_sort_map["heal_bonus"] = percent_to_float(card_sort_map["治疗效果加成"])

        card_sort_map["echo_id"] = result.get("echo_id")
        # logger.debug(f"面板数据: {card_sort_map}")
        return card_sort_map

    def card_sort_map_to_attribute(self, card_sort_map: Dict):
        attr = DamageAttribute(
            enemy_resistance=self.enemy_detail.enemy_resistance / 100,
            enemy_level=self.enemy_detail.enemy_level,
        )
        attr.set_char_atk(card_sort_map["char_atk"])
        attr.set_char_life(card_sort_map["char_life"])
        attr.set_char_def(card_sort_map["char_def"])
        attr.set_weapon_atk(card_sort_map["weapon_atk"])
        attr.set_atk_flat(card_sort_map["atk_flat"])
        attr.set_life_flat(card_sort_map["life_flat"])
        attr.set_def_flat(card_sort_map["def_flat"])
        attr.add_atk_percent(card_sort_map["atk_percent"])
        attr.add_life_percent(card_sort_map["life_percent"])
        attr.add_def_percent(card_sort_map["def_percent"])
        attr.add_crit_rate(card_sort_map["crit_rate"])
        attr.add_crit_dmg(card_sort_map["crit_dmg"])
        attr.add_energy_regen(card_sort_map["energy_regen"])
        # attr.add_dmg_bonus(card_sort_map['dmg_bonus'])
        attr.set_dmg_bonus_phantom(card_sort_map)
        attr.set_echo_id(card_sort_map["echo_id"])
        attr.set_char_attr(card_sort_map["char_attr"])
        if card_sort_map.get("ph_detail"):
            for ph_detail in card_sort_map["ph_detail"]:
                attr.add_ph_detail(ph_detail)
        attr.set_ph_result(card_sort_map["ph_result"])
        attr.set_role(self.role_detail)
        return attr
