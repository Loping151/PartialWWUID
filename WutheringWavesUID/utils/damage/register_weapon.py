from typing import List, Union

from ..damage.abstract import WavesWeaponRegister, WeaponAbstract
from .damage import DamageAttribute, calc_percent_expression
from .utils import (
    CHAR_ATTR_CELESTIAL,
    CHAR_ATTR_MOLTEN,
    CHAR_ATTR_SIERRA,
    Spectro_Frazzle_Role_Ids,
    attack_damage,
    heal_bonus,
    hit_damage,
    liberation_damage,
    phantom_damage,
    skill_damage,
    temp_atk,
    temp_def,
    temp_life,
)


class Weapon_21010011(WeaponAbstract):
    id = 21010011
    type = 1
    name = "教学长刃"


class Weapon_21010012(WeaponAbstract):
    id = 21010012
    type = 1
    name = "原初长刃·朴石"


class Weapon_21010013(WeaponAbstract):
    id = 21010013
    type = 1
    name = "暗夜长刃·玄明"


class Weapon_21010015(WeaponAbstract):
    id = 21010015
    type = 1
    name = "浩境粼光"

    # 施放共鸣技能时，共鸣解放伤害加成提升7%，可叠加3层，持续12秒
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_damage != liberation_damage:
            return
        dmg = f"{self.param(1)}*{self.param(2)}"
        title = self.get_title()
        msg = f"施放共鸣技能时，共鸣解放伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21010016(WeaponAbstract):
    id = 21010016
    type = 1
    name = "苍鳞千嶂"

    # 每次施放变奏技能或共鸣解放时，自身重击伤害加成提升{1}，可叠加{2}层

    def cast_variation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放变奏技能"""
        if attr.char_damage != hit_damage:
            return
        dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}"
        title = self.get_title()
        msg = f"施放变奏技能时，自身重击伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_damage != hit_damage:
            return
        dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}"
        title = self.get_title()
        msg = f"施放共鸣解放时，自身重击伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21010023(WeaponAbstract):
    id = 21010023
    type = 1
    name = "源能长刃·测壹"


class Weapon_21010024(WeaponAbstract):
    id = 21010024
    type = 1
    name = "异响空灵"


class Weapon_21010026(WeaponAbstract):
    id = 21010026
    type = 1
    name = "时和岁稔"

    def cast_variation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放变奏技能"""
        if attr.char_damage != skill_damage:
            return
        # 施放变奏技能时，自身获得【岁蕴】，使共鸣技能伤害加成提升24%
        dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}"
        title = self.get_title()
        msg = f"施放变奏技能时，使共鸣技能伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_damage != skill_damage:
            return

        # 施放共鸣技能时，自身获得【福泽】，使共鸣技能伤害加成提升24%
        dmg = f"{self.weapon_detail.param[3][self.weapon_reson_level - 1]}"
        title = self.get_title()
        msg = f"施放共鸣技能时，使共鸣技能伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21010034(WeaponAbstract):
    id = 21010034
    type = 1
    name = "重破刃-41型"

    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        # 生命大于80%时，攻击提升12%。
        if attr.char_template == temp_atk:
            dmg = f"{self.param(1)}"
            title = self.get_title()
            msg = f"生命大于{self.param(0)}时，攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21010036(WeaponAbstract):
    id = 21010036
    type = 1
    name = "焰痕"

    # 攻击提升12%。施放变奏技能或共鸣解放时，共鸣解放伤害提升24%，持续6秒；造成重击伤害时，该效果延长4秒，最多可延长1次。成功延长效果时，使队伍中的角色热熔伤害加成提升24%，持续30秒，同名效果之间不可叠加。

    def cast_variation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放变奏技能"""
        if attr.char_damage != liberation_damage:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放变奏技能时，共鸣解放伤害提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True

    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_damage != liberation_damage:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放共鸣解放时，共鸣解放伤害提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True

    def cast_hit(self, attr: DamageAttribute, isGroup: bool = False):
        """施放重击伤害"""
        if attr.char_attr != CHAR_ATTR_MOLTEN:
            return
        dmg = f"{self.param(5)}"
        title = self.get_title()
        msg = f"施放重击伤害时，使队伍中的角色热熔伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21010043(WeaponAbstract):
    id = 21010043
    type = 1
    name = "远行者长刃·辟路"


class Weapon_21010044(WeaponAbstract):
    id = 21010044
    type = 1
    name = "永夜长明"

    def cast_variation(
        self,
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        """施放变奏技能"""
        # 施放变奏技能时，自身攻击提升8%，防御提升15%
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}"
            title = self.get_title()
            msg = f"施放变奏技能时，自身攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)

        if attr.char_template == temp_def:
            dmg = f"{self.param(1)}"
            title = self.get_title()
            msg = f"施放变奏技能时，自身防御提升{dmg}"
            attr.add_def_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21010046(WeaponAbstract):
    id = 21010046
    type = 1
    name = "驭冕铸雷之权"

    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_damage != hit_damage:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放共鸣技能时，重击伤害提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

    def trigger_shield(self, attr: DamageAttribute, isGroup: bool = False):
        """触发护盾"""
        if attr.char_damage != hit_damage:
            return
        dmg = f"{self.param(3)}*{self.param(4)}"
        title = self.get_title()
        msg = f"自身获得护盾时，重击伤害无视目标{dmg}防御"
        attr.add_defense_reduction(calc_percent_expression(dmg), title, msg)


class Weapon_21010053(WeaponAbstract):
    id = 21010053
    type = 1
    name = "戍关长刃·定军"


class Weapon_21010056(WeaponAbstract):
    id = 21010056
    type = 1
    name = "昙切"

    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        # 施放变奏技能或附加【异常效应】时才生效
        if not attr.is_env_abnormal:
            return

        if attr.char_damage != liberation_damage:
            return

        title = self.get_title()
        dmg = f"{self.param(1)}*{self.param(2)}"
        msg = f"施放变奏技能或附加【异常效应】时，共鸣解放伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

        # 千咲：满层时，附加异常效应时全属性伤害加成
        if attr.role and attr.role.role.roleId == 1508:
            dmg2 = f"{self.param(4)}"
            msg = f"满层时附加【异常效应】，全属性伤害加成提升{dmg2}"
            attr.add_dmg_bonus(calc_percent_expression(dmg2), title, msg)


class Weapon_21010063(WeaponAbstract):
    id = 21010063
    type = 1
    name = "钧天正音"


class Weapon_21010064(WeaponAbstract):
    id = 21010064
    type = 1
    name = "东落"

    # 施放共鸣技能后12秒内，每2秒攻击提升3%，可叠加4层。
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_template == temp_atk:
            dmg = f"{self.param(2)}*{self.param(3)}"
            title = self.get_title()
            msg = f"施放共鸣技能后，每2秒攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21010074(WeaponAbstract):
    id = 21010074
    type = 1
    name = "纹秋"

    # 造成普攻或重击伤害时，攻击提升4%，可叠加5层
    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}*{self.param(1)}"
            title = self.get_title()
            msg = f"施放普攻时，自身攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)
            return True

    def cast_hit(self, attr: DamageAttribute, isGroup: bool = False):
        """施放重击伤害"""
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}*{self.param(1)}"
            title = self.get_title()
            msg = f"施放重击伤害时，自身攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)
            return True


class Weapon_21010084(WeaponAbstract):
    id = 21010084
    type = 1
    name = "凋亡频移"

    # 施放共鸣技能时，获得6点共鸣能量，且攻击提升10%，持续16秒。
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_template != temp_atk:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放共鸣技能时，获得{self.param(0)}点共鸣能量，且攻击提升{dmg}"
        attr.add_atk_percent(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21010094(WeaponAbstract):
    id = 21010094
    type = 1
    name = "容赦的沉思录"

    # 对带有【异常效应】的怪物造成伤害时，自身攻击提升4%，持续10秒，每秒可触发1次，可叠加4层。
    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        if not attr.is_env_abnormal:
            return
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}*{self.param(2)}"
            title = self.get_title()
            msg = f"对带有【异常效应】的怪物造成伤害时，自身攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21010104(WeaponAbstract):
    id = 21010104
    type = 1
    name = "金穹"

    # 施放共鸣解放时，攻击提升7.2%，重击伤害加成提升10.8%
    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}"
            title = self.get_title()
            msg = f"施放共鸣解放时，攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)

        if attr.char_damage == hit_damage:
            dmg = f"{self.param(1)}"
            title = self.get_title()
            msg = f"施放共鸣解放时，重击伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21020011(WeaponAbstract):
    id = 21020011
    type = 2
    name = "教学迅刀"


class Weapon_21020012(WeaponAbstract):
    id = 21020012
    type = 2
    name = "原初迅刀·鸣雨"


class Weapon_21020013(WeaponAbstract):
    id = 21020013
    type = 2
    name = "暗夜迅刀·黑闪"


class Weapon_21020015(WeaponAbstract):
    id = 21020015
    type = 2
    name = "千古洑流"

    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_template == temp_atk:
            dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}*{self.weapon_detail.param[2][self.weapon_reson_level - 1]}"
            title = self.get_title()
            msg = f"施放共鸣技能时，攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)
            return True


class Weapon_21020016(WeaponAbstract):
    id = 21020016
    type = 2
    name = "赫奕流明"

    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """造成共鸣技能伤害"""
        if attr.char_damage != skill_damage:
            return

        dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}*14"
        title = self.get_title()
        msg = f"每层【灼羽】使共鸣技能伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21020017(WeaponAbstract):
    id = 21020017
    type = 2
    name = "心之锚"

    def _damage(self, attr: DamageAttribute, isGroup: bool = False):
        """造成伤害"""
        title = self.get_title()

        if attr.char_template == temp_atk:
            dmg1 = f"{self.weapon_detail.param[3][self.weapon_reson_level - 1]}*{self.weapon_detail.param[5][self.weapon_reson_level - 1]}"
            attr.add_atk_percent(calc_percent_expression(dmg1))
            msg = f"【凶猛】为10层时，攻击提升{dmg1}"
            attr.add_effect(title, msg)

        dmg2 = f"{self.weapon_detail.param[7][self.weapon_reson_level - 1]}"
        attr.add_crit_rate(calc_percent_expression(dmg2))
        title = self.get_title()
        msg = f"【凶猛】为10层时， 暴击率提升{dmg2}"
        attr.add_effect(title, msg)

    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """施放普攻"""
        self._damage(attr, isGroup)
        return True

    def cast_hit(self, attr: DamageAttribute, isGroup: bool = False):
        """施放重击"""
        self._damage(attr, isGroup)
        return True

    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        self._damage(attr, isGroup)
        return True

    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        self._damage(attr, isGroup)
        return True


class Weapon_21020023(WeaponAbstract):
    id = 21020023
    type = 2
    name = "源能迅刀·测贰"


class Weapon_21020024(WeaponAbstract):
    id = 21020024
    type = 2
    name = "行进序曲"


class Weapon_21020026(WeaponAbstract):
    id = 21020026
    type = 2
    name = "裁春"

    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """造成普攻伤害"""
        if attr.char_damage != attack_damage:
            return
        if attr.role and attr.role.role.roleId == 1603:
            dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}*{self.weapon_detail.param[3][self.weapon_reson_level - 1]}+{self.weapon_detail.param[4][self.weapon_reson_level - 1]}"
        else:
            dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}*{self.weapon_detail.param[3][self.weapon_reson_level - 1]}"
        title = self.get_title()
        msg = f"普攻伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21020034(WeaponAbstract):
    id = 21020034
    type = 2
    name = "瞬斩刀-18型"

    # 生命低于40%时，重击伤害加成提升18%

    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        if attr.char_damage == hit_damage:
            dmg = f"{self.param(1)}"
            title = self.get_title()
            msg = f"生命低于{self.param(0)}时，重击伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21020036(WeaponAbstract):
    id = 21020036
    type = 2
    name = "不灭航路"

    # 施放共鸣解放后，普攻伤害加成提高48%，持续10秒。造成普攻伤害时，普攻伤害加成提升48%
    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """造成普攻伤害"""
        if attr.char_damage != attack_damage:
            return

        dmg = f"{self.param(3)}"
        title = self.get_title()
        msg = f"造成普攻伤害时，普攻伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_damage != attack_damage:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放共鸣解放后，普攻伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21020043(WeaponAbstract):
    id = 21020043
    type = 2
    name = "远行者迅刀·旅迹"


class Weapon_21020044(WeaponAbstract):
    id = 21020044
    type = 2
    name = "不归孤军"

    def cast_variation(
        self,
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        """施放变奏技能"""
        # 施放变奏技能时，自身攻击提升15%
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}"
            title = self.get_title()
            msg = f"施放变奏技能时，自身攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21020046(WeaponAbstract):
    id = 21020046
    type = 2
    name = "血誓盟约"

    def cast_healing(self, attr: DamageAttribute, isGroup: bool = False):
        """施放治疗"""
        if attr.char_damage != skill_damage:
            return
        dmg = f"{self.param(0)}"
        title = self.get_title()
        msg = f"造成治疗时，自身共鸣技能伤害提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_attr != CHAR_ATTR_SIERRA:
            return
        if attr.role and attr.role.role.roleId in [1406, 1408]:
            dmg = f"{self.param(2)}"
            title = self.get_title()
            msg = f"风主施放共鸣技能时，附近队伍中登场角色气动伤害加深{dmg}"
            attr.add_dmg_deepen(calc_percent_expression(dmg), title, msg)


class Weapon_21020053(WeaponAbstract):
    id = 21020053
    type = 2
    name = "戍关迅刀·镇海"


class Weapon_21020056(WeaponAbstract):
    id = 21020056
    type = 2
    name = "不屈命定之冠"

    # 施放变奏技能或普攻后15秒内，自身造成伤害无视目标8%防御，当目标的风蚀效应不少于1层时，对目标造成的伤害加深20%。
    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.env_aero_erosion:
            dmg = f"{self.param(2)}"
            title = self.get_title()
            msg = f"当目标的风蚀效应不少于1层时，对目标造成的伤害加深{dmg}"
            attr.add_dmg_deepen(calc_percent_expression(dmg), title, msg)

        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放变奏技能或普攻后15秒内，自身造成伤害无视目标{dmg}防御"
        attr.add_defense_reduction(calc_percent_expression(dmg), title, msg)


class Weapon_21020064(WeaponAbstract):
    id = 21020064
    type = 2
    name = "西升"

    # 角色登场后获得6层【守誓】效果，每层使攻击提升2%
    # ps: 不计算击败目标

    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        if attr.char_template == temp_atk:
            dmg = f"{self.param(1)}*{self.param(2)}"
            title = self.get_title()
            msg = f"角色登场后获得{self.param(0)}层【守誓】效果，使攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21020066(WeaponAbstract):
    id = 21020066
    type = 2
    name = "裁竹"

    # 施放变奏技能或普攻后10秒内，施放声骸技能时，获得1层【解竹】，重击伤害加成提升30%，同名声骸只可触发一次，最多可叠加2层，持续12秒，叠加至2层后施放声骸技能不刷新持续时间。该效果10秒内最多生效1次，若切换至其他角色则该效果提前结束。
    # 施放变奏技能时，队伍中的角色声骸技能伤害加成提升20%，持续30秒，同名效果之间不可叠加。
    def cast_phantom(self, attr: DamageAttribute, isGroup: bool = False):
        """施放声骸技能"""
        if attr.char_damage == hit_damage:
            dmg = f"{self.param(2)}%*2"
            title = self.get_title()
            msg = f"施放声骸技能时，重击伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21020074(WeaponAbstract):
    id = 21020074
    type = 2
    name = "飞景"

    # 施放共鸣技能时，自身普攻和重击伤害加成提升20%。
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_damage == attack_damage:
            dmg = f"{self.param(0)}*{self.param(1)}"
            title = self.get_title()
            msg = f"施放共鸣技能时，自身普攻加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

        if attr.char_damage == hit_damage:
            dmg = f"{self.param(0)}*{self.param(1)}"
            title = self.get_title()
            msg = f"施放共鸣技能时，自身重击加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21020084(WeaponAbstract):
    id = 21020084
    type = 2
    name = "永续坍缩"

    # 施放共鸣技能时，获得6点共鸣能量，且攻击提升10%，持续16秒。
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_template != temp_atk:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放共鸣技能时，获得{self.param(0)}点共鸣能量，且攻击提升{dmg}"
        attr.add_atk_percent(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21020094(WeaponAbstract):
    id = 21020094
    type = 2
    name = "风流的寓言诗"

    # 对带有【异常效应】的怪物造成伤害时，自身攻击提升4%，持续10秒，每秒可触发1次，可叠加4层。
    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        if not attr.is_env_abnormal:
            return
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}*{self.param(2)}"
            title = self.get_title()
            msg = f"对带有【异常效应】的怪物造成伤害时，自身攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21020104(WeaponAbstract):
    id = 21020104
    type = 2
    name = "翼锋"

    # 施放共鸣解放时，攻击提升7.2%，共鸣解放伤害加成提升10.8%
    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_damage == liberation_damage:
            dmg = f"{self.param(1)}"
            title = self.get_title()
            msg = f"施放共鸣解放时，共鸣解放伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}"
            title = self.get_title()
            msg = f"施放共鸣解放时，攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21030011(WeaponAbstract):
    id = 21030011
    type = 3
    name = "教学佩枪"


class Weapon_21030012(WeaponAbstract):
    id = 21030012
    type = 3
    name = "原初佩枪·穿林"


class Weapon_21030013(WeaponAbstract):
    id = 21030013
    type = 3
    name = "暗夜佩枪·暗星"


class Weapon_21030015(WeaponAbstract):
    id = 21030015
    type = 3
    name = "停驻之烟"

    def buff(self, attr: DamageAttribute, isGroup: bool = False):
        """造成伤害"""
        if isGroup:
            if attr.char_template == temp_atk:
                dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}*{self.weapon_detail.param[2][self.weapon_reson_level - 1]}"
                title = self.get_title()
                msg = f"施放延奏技能后，入场角色攻击提升{dmg}"
                attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21030016(WeaponAbstract):
    id = 21030016
    type = 3
    name = "死与舞"

    # 施放变奏技能或共鸣解放时，自身共鸣技能伤害加成提升48%

    def cast_variation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放变奏技能"""
        if attr.char_damage != skill_damage:
            return
        dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}"
        title = self.get_title()
        msg = f"施放变奏技能时，自身共鸣技能伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True

    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_damage != skill_damage:
            return
        dmg = f"{self.weapon_detail.param[1][self.weapon_reson_level - 1]}"
        title = self.get_title()
        msg = f"施放共鸣解放时，自身共鸣技能伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21030023(WeaponAbstract):
    id = 21030023
    type = 3
    name = "源能佩枪·测叁"


class Weapon_21030024(WeaponAbstract):
    id = 21030024
    type = 3
    name = "华彩乐段"


class Weapon_21030026(WeaponAbstract):
    id = 21030026
    type = 3
    name = "林间的咏叹调"

    def env_aero_erosion(self, attr: DamageAttribute, isGroup: bool = False):
        """风蚀效应"""
        if attr.char_attr != CHAR_ATTR_SIERRA:
            return

        # 为目标添加【风蚀效应】后，自身气动伤害加成提升24%。
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"为目标添加【风蚀效应】后，自身气动伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

        # 攻击命中带有【风蚀效应】的敌人时，降低对方10%的气动抗性
        dmg = f"{self.param(3)}"
        title = self.get_title()
        msg = f"攻击命中带有【风蚀效应】的敌人时，降低对方{dmg}的气动抗性"
        attr.add_enemy_resistance(-calc_percent_expression(dmg), title, msg)


class Weapon_21030034(WeaponAbstract):
    id = 21030034
    type = 3
    name = "穿击枪-26型"


class Weapon_21030043(WeaponAbstract):
    id = 21030043
    type = 3
    name = "远行者佩枪·洞察"


class Weapon_21030036(WeaponAbstract):
    id = 21030036
    type = 3
    name = "光影双生"

    # 攻击提升12%。造成声骸技能伤害时，重击伤害加深24%，持续6秒；造成重击伤害时，声骸技能伤害加深24%，持续6秒；单次攻击最多享受24%伤害加深。同时拥有两种效果时，造成伤害时无视目标8%防御。
    def cast_phantom(self, attr: DamageAttribute, isGroup: bool = False):
        """施放声骸技能"""
        if attr.char_damage != hit_damage:
            return False
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"造成声骸技能伤害时，重击伤害加深{dmg}"
        attr.add_dmg_deepen(calc_percent_expression(dmg), title, msg)

        # 嘉贝莉娜
        if attr.role and attr.role.role.roleId == 1208:
            dmg = f"{self.param(6)}"
            title = self.get_title()
            msg = f"无视目标{dmg}防御"
            attr.add_defense_reduction(calc_percent_expression(dmg), title, msg)

        return True

    def cast_hit(self, attr: DamageAttribute, isGroup: bool = False):
        """施放重击"""
        if attr.char_damage != phantom_damage:
            return False
        dmg = f"{self.param(3)}"
        title = self.get_title()
        msg = f"造成重击伤害时，声骸技能伤害加深{dmg}"
        attr.add_dmg_deepen(calc_percent_expression(dmg), title, msg)

        # 嘉贝莉娜
        if attr.role and attr.role.role.roleId == 1208:
            dmg = f"{self.param(6)}"
            title = self.get_title()
            msg = f"无视目标{dmg}防御"
            attr.add_defense_reduction(calc_percent_expression(dmg), title, msg)

        return True


class Weapon_21030044(WeaponAbstract):
    id = 21030044
    type = 3
    name = "无眠烈火"


class Weapon_21030053(WeaponAbstract):
    id = 21030053
    type = 3
    name = "戍关佩枪·平云"


class Weapon_21030064(WeaponAbstract):
    id = 21030064
    type = 3
    name = "飞逝"

    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        # 角色冲刺或闪避时，攻击提升4%，持续8秒，可叠加3层。
        if attr.char_template != temp_atk:
            return

        dmg = f"{self.param(0)}*{self.param(2)}"
        title = self.get_title()
        msg = f"角色冲刺或闪避时，攻击提升{dmg}"
        attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21030074(WeaponAbstract):
    id = 21030074
    type = 3
    name = "奔雷"

    # 造成普攻或重击伤害时，自身共鸣技能伤害加成提升7%，可叠加3层，持续10秒。
    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """施放普攻"""
        if attr.char_damage != skill_damage:
            return
        dmg = f"{self.param(0)}*{self.param(1)}"
        title = self.get_title()
        msg = f"造成普攻或重击伤害时，自身共鸣技能伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True

    def cast_hit(self, attr: DamageAttribute, isGroup: bool = False):
        """施放重击"""
        if attr.char_damage != skill_damage:
            return
        dmg = f"{self.param(0)}*{self.param(1)}"
        title = self.get_title()
        msg = f"造成普攻或重击伤害时，自身共鸣技能伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21030084(WeaponAbstract):
    id = 21030084
    type = 3
    name = "悖论喷流"

    # 施放共鸣技能时，获得6点共鸣能量，且攻击提升10%，持续16秒。
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_template != temp_atk:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放共鸣技能时，获得{self.param(0)}点共鸣能量，且攻击提升{dmg}"
        attr.add_atk_percent(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21030094(WeaponAbstract):
    id = 21030094
    type = 3
    name = "叙别的罗曼史"

    # 对带有【异常效应】的怪物造成伤害时，自身攻击提升4%，持续10秒，每秒可触发1次，可叠加4层。
    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        if not attr.is_env_abnormal:
            return
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}*{self.param(2)}"
            title = self.get_title()
            msg = f"对带有【异常效应】的怪物造成伤害时，自身攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21030104(WeaponAbstract):
    id = 21030104
    type = 3
    name = "阳焰"

    # 造成普攻或重击伤害时，攻击和重击伤害加成提升2.2%，可叠加4层
    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """施放普攻"""
        if attr.char_damage == hit_damage:
            dmg = f"{self.param(0)}*{self.param(1)}"
            title = self.get_title()
            msg = f"造成普攻伤害时，重击伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

        if attr.char_damage == attack_damage:
            dmg = f"{self.param(0)}*{self.param(1)}"
            title = self.get_title()
            msg = f"造成普攻伤害时，攻击伤害加成提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)
        return True

    def cast_hit(self, attr: DamageAttribute, isGroup: bool = False):
        """施放重击"""
        if attr.char_damage == hit_damage:
            dmg = f"{self.param(0)}*{self.param(1)}"
            title = self.get_title()
            msg = f"造成重击伤害时，重击伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

        if attr.char_damage == attack_damage:
            dmg = f"{self.param(0)}*{self.param(1)}"
            title = self.get_title()
            msg = f"造成重击伤害时，攻击伤害加成提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21040011(WeaponAbstract):
    id = 21040011
    type = 4
    name = "教学臂铠"


class Weapon_21040012(WeaponAbstract):
    id = 21040012
    type = 4
    name = "原初臂铠·磐岩"


class Weapon_21040013(WeaponAbstract):
    id = 21040013
    type = 4
    name = "暗夜臂铠·夜芒"


class Weapon_21040015(WeaponAbstract):
    id = 21040015
    type = 4
    name = "擎渊怒涛"

    # 造成共鸣技能伤害时，普攻伤害加成提升10%，持续8秒。造成普攻伤害时，共鸣技能伤害加成提升10%，持续8秒。
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_damage != attack_damage:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"造成共鸣技能伤害时，普攻伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """造成普攻伤害"""
        if attr.char_damage != skill_damage:
            return

        dmg = f"{self.param(3)}"
        title = self.get_title()
        msg = f"造成普攻伤害时，共鸣技能伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21040016(WeaponAbstract):
    id = 21040016
    type = 4
    name = "诸方玄枢"

    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_damage != liberation_damage:
            return

        # 施放共鸣解放时，自身共鸣解放伤害加成提升48%，持续8秒；施放共鸣技能时，该效果延长5秒，最多可延长3次。
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放共鸣解放时，自身共鸣解放伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21040023(WeaponAbstract):
    id = 21040023
    type = 4
    name = "源能臂铠·测肆"


class Weapon_21040024(WeaponAbstract):
    id = 21040024
    type = 4
    name = "呼啸重音"


class Weapon_21040026(WeaponAbstract):
    id = 21040026
    type = 4
    name = "悲喜剧"

    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """施放普攻"""
        if attr.char_damage != hit_damage:
            return

        # 攻击提升12%。施放普攻或变奏技能时，自身重击伤害加成提升48%，持续3秒。
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放普攻技能时，自身重击伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True

    def cast_variation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放变奏技能"""
        if attr.char_damage != hit_damage:
            return

        # 攻击提升12%。施放普攻或变奏技能时，自身重击伤害加成提升48%，持续3秒。
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放变奏技能时，自身重击伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21040034(WeaponAbstract):
    id = 21040034
    type = 4
    name = "钢影拳-21丁型"

    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        # 闪避或冲刺时，攻击提升8%。
        if attr.char_template != temp_atk:
            return

        dmg = f"{self.param(0)}"
        title = self.get_title()
        msg = f"冲刺或冲刺时，攻击提升{dmg}"
        attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21040036(WeaponAbstract):
    id = 21040036
    type = 4
    name = "焰光裁定"

    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """施放普攻"""
        # 攻击提升12%。施放普攻时，获得以下效果：自身造成伤害无视目标8%防御。
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放普攻技能时，自身造成伤害无视目标{dmg}防御"
        attr.add_defense_reduction(calc_percent_expression(dmg), title, msg)

        if attr.env_spectro_deepen:
            dmg = f"{self.param(2)}"
            title = self.get_title()
            msg = f"自身直接造成的【光噪效应】伤害加深{dmg}"
            attr.add_dmg_deepen(calc_percent_expression(dmg), title, msg)


class Weapon_21040043(WeaponAbstract):
    id = 21040043
    type = 4
    name = "远行者臂铠·破障"


class Weapon_21040044(WeaponAbstract):
    id = 21040044
    type = 4
    name = "袍泽之固"

    # 施放变奏技能时，自身共鸣解放伤害加成提升20%
    def cast_variation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放变奏技能"""
        if attr.char_damage != liberation_damage:
            return
        dmg = f"{self.param(0)}"
        title = self.get_title()
        msg = f"施放变奏技能时，自身共鸣解放伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21040046(WeaponAbstract):
    id = 21040046
    type = 4
    name = "万物持存的注释"

    # 施放变奏技能或共鸣解放时，共鸣解放伤害提升20%，持续15秒。
    # 自身获得护盾时：共鸣解放伤害无视目标7.2%防御，每0.5秒可生效1次，可叠加5层，持续7秒；
    # 施放变奏技能时，无视目标防御的效果视为满层，持续3秒。
    def cast_variation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放变奏技能"""
        if attr.char_damage != liberation_damage:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放变奏技能时，自身共鸣解放伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

        dmg = f"{self.param(3)}*{self.param(5)}"
        title = self.get_title()
        msg = f"自身获得护盾时，共鸣解放伤害无视目标{dmg}防御"
        attr.add_defense_reduction(calc_percent_expression(dmg), title, msg)

        return True

    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_damage != liberation_damage:
            return
        if not attr.trigger_shield:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放共鸣解放时，自身共鸣解放伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

        dmg = f"{self.param(3)}*{self.param(5)}"
        title = self.get_title()
        msg = f"自身获得护盾时，共鸣解放伤害无视目标{dmg}防御"
        attr.add_defense_reduction(calc_percent_expression(dmg), title, msg)

        return True


class Weapon_21040053(WeaponAbstract):
    id = 21040053
    type = 4
    name = "戍关臂铠·拔山"


class Weapon_21040064(WeaponAbstract):
    id = 21040064
    type = 4
    name = "骇行"

    # 施放共鸣解放时，获得3层【铁甲】效果，每层使攻击和防御提升3%
    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_template == temp_atk:
            dmg = f"{self.param(1)}*{self.param(0)}"
            title = self.get_title()
            msg = f"施放共鸣解放时，获得3层【铁甲】效果，使攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)

        dmg = f"{self.param(1)}*{self.param(0)}"
        title = self.get_title()
        msg = f"施放共鸣解放时，获得3层【铁甲】效果，使防御提升{dmg}"
        attr.add_def_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21040074(WeaponAbstract):
    id = 21040074
    type = 4
    name = "金掌"

    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_damage != liberation_damage:
            return
        dmg = f"{self.param(0)}"
        title = self.get_title()
        msg = f"施放共鸣技能时，自身共鸣解放伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21040084(WeaponAbstract):
    id = 21040084
    type = 4
    name = "尘云旋臂"

    # 施放共鸣技能时，获得6点共鸣能量，且攻击提升10%，持续16秒。
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_template != temp_atk:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放共鸣技能时，获得{self.param(0)}点共鸣能量，且攻击提升{dmg}"
        attr.add_atk_percent(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21040094(WeaponAbstract):
    id = 21040094
    type = 4
    name = "酩酊的英雄志"

    # 对带有【异常效应】的怪物造成伤害时，自身攻击提升4%，持续10秒，每秒可触发1次，可叠加4层。
    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        if not attr.is_env_abnormal:
            return
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}*{self.param(2)}"
            title = self.get_title()
            msg = f"对带有【异常效应】的怪物造成伤害时，自身攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21040104(WeaponAbstract):
    id = 21040104
    type = 4
    name = "凌空"

    # 施放共鸣解放时，攻击提升7.2%，共鸣解放伤害加成提升10.8%
    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}"
            title = self.get_title()
            msg = f"施放共鸣解放时，攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)

        if attr.char_damage == liberation_damage:
            dmg = f"{self.param(1)}"
            title = self.get_title()
            msg = f"施放共鸣解放时，共鸣解放伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21050011(WeaponAbstract):
    id = 21050011
    type = 5
    name = "教学音感仪"


class Weapon_21050012(WeaponAbstract):
    id = 21050012
    type = 5
    name = "原初音感仪·听浪"


class Weapon_21050013(WeaponAbstract):
    id = 21050013
    type = 5
    name = "暗夜矩阵·暝光"


class Weapon_21050015(WeaponAbstract):
    id = 21050015
    type = 5
    name = "漪澜浮录"

    # 造成普攻伤害时，普攻伤害加成提升3.2%，可叠加5层
    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """施放普攻"""
        if attr.char_damage != attack_damage:
            return

        dmg = f"{self.param(1)}*{self.param(2)}"
        title = self.get_title()
        msg = f"造成普攻伤害时，普攻伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21050016(WeaponAbstract):
    id = 21050016
    type = 5
    name = "掣傀之手"

    # 造成共鸣技能伤害时，自身攻击提升12%，可叠加2层，效果持续5秒。自身不在场时，该效果攻击额外提升12%。

    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_template != temp_atk:
            return

        dmg1 = f"{self.param(1)}*{self.param(2)}"
        title = self.get_title()
        msg = f"造成共鸣技能伤害时，自身攻击提升{dmg1}"
        attr.add_atk_percent(calc_percent_expression(dmg1), title, msg)
        if attr.sync_strike:
            dmg2 = f"{self.param(4)}"
            msg = f"自身不在场时，该效果攻击额外提升{dmg2}"
            attr.add_atk_percent(calc_percent_expression(dmg2), title, msg)


class Weapon_21050017(WeaponAbstract):
    id = 21050017
    type = 5
    name = "渊海回声"

    # 施放共鸣解放时，自身治疗效果加成提升16%
    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_damage != heal_bonus:
            return

        dmg = f"{self.param(0)}"
        title = self.get_title()
        msg = f"施放共鸣解放时，自身治疗效果加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21050023(WeaponAbstract):
    id = 21050023
    type = 5
    name = "源能音感仪·测五"


class Weapon_21050024(WeaponAbstract):
    id = 21050024
    type = 5
    name = "奇幻变奏"


class Weapon_21050026(WeaponAbstract):
    id = 21050026
    type = 5
    name = "琼枝冰绡"

    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_damage != attack_damage:
            return

        if attr.sync_strike:
            dmg = f"{self.param(5)}"
            title = self.get_title()
            msg = f"使自身不在场时普攻伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        else:
            buff_layer = int(self.param(2))
            effect_value = attr.get_effect("默认手法")
            if effect_value and isinstance(effect_value, str):
                count_e = effect_value.count("e")

                buff_layer = min(buff_layer, count_e)
            else:
                buff_layer = 1

            dmg = f"{self.param(1)}*{buff_layer}"
            title = self.get_title()
            msg = f"施放共鸣技能时，自身在场时普攻伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21050027(WeaponAbstract):
    id = 21050027
    type = 5
    name = "大海的馈赠"

    # 对带有【光噪效应】的敌人造成伤害时获得效果：自身衍射伤害提升6%，每1秒可获得1层，持续6秒，可叠加4层。
    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        if not attr.env_spectro:
            return
        if attr.char_attr != CHAR_ATTR_CELESTIAL:
            return
        dmg = f"{self.param(0)*4}"
        title = self.get_title()
        msg = f"对带有【光噪效应】的敌人造成伤害时获得效果：自身衍射伤害提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21050034(WeaponAbstract):
    id = 21050034
    type = 5
    name = "鸣动仪-25型"

    # 施放共鸣技能时，若角色生命低于60%，回复角色5%生命值，每8秒可触发1次；若角色生命高于60%，则攻击提升12%，持续10秒。
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_template != temp_atk:
            return
        dmg = f"{self.param(5)}"
        title = self.get_title()
        msg = f"施放共鸣技能时，若角色生命高于{self.param(4)}，则攻击提升{dmg}"
        attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21050036(WeaponAbstract):
    id = 21050036
    type = 5
    name = "星序协响"

    def skill_create_healing(self, attr: DamageAttribute, isGroup: bool = False):
        """共鸣技能造成治疗"""
        if attr.char_template != temp_atk:
            return
        dmg = f"{self.weapon_detail.param[4][self.weapon_reson_level - 1]}"
        title = self.get_title()
        msg = f"使附近队伍中所有角色的攻击提升{dmg}"
        attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21050043(WeaponAbstract):
    id = 21050043
    type = 5
    name = "远行者矩阵·探幽"


class Weapon_21050044(WeaponAbstract):
    id = 21050044
    type = 5
    name = "今州守望"

    # 施放变奏技能时，自身攻击提升8%，生命提升10%
    def cast_variation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放变奏技能"""
        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}"
            title = self.get_title()
            msg = f"施放变奏技能时，自身攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)

        if attr.char_template == temp_life:
            dmg = f"{self.param(1)}"
            title = self.get_title()
            msg = f"施放变奏技能时，自身生命提升{dmg}"
            attr.add_life_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21050046(WeaponAbstract):
    id = 21050046
    type = 5
    name = "和光回唱"

    def check_1(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.role is None:
            return False
        return attr.role.role.roleId not in Spectro_Frazzle_Role_Ids

    def check_2(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.role is None:
            return False
        if not isGroup:
            return False
        if not attr.teammate_char_ids:
            return False
        return any(x in Spectro_Frazzle_Role_Ids for x in attr.teammate_char_ids)

    def env_spectro(self, attr: DamageAttribute, isGroup: bool = False):
        """光噪效应"""
        if attr.char_damage != hit_damage and attr.char_damage != attack_damage:
            return

        # 对附加了【光噪效应】的目标造成伤害时，自身普攻、重击伤害加成提升14%，可以叠加3层。
        dmg = f"{self.param(1)}*{self.param(2)}"
        title = self.get_title()
        msg = f"光噪效应状态下，自身普攻、重击伤害加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

    def cast_extension(self, attr: DamageAttribute, isGroup: bool = False):
        """施放延奏技能"""
        if not isGroup:
            return

        if not attr.env_spectro_deepen:
            return

        # 施放延奏技能时，使队伍中登场角色周围的目标受到【光噪效应】伤害加深30%，持续30秒
        dmg = f"{self.param(4)}"
        title = self.get_title()
        msg = f"施放延奏技能时，使登场角色【光噪效应】伤害加深{dmg}"
        attr.add_dmg_deepen(calc_percent_expression(dmg), title, msg)


class Weapon_21050053(WeaponAbstract):
    id = 21050053
    type = 5
    name = "戍关音感仪·留光"


class Weapon_21050056(WeaponAbstract):
    id = 21050056
    type = 5
    name = "海的呢喃"

    """
    攻击提升12%。施放变奏技能或普攻后10秒内，施放声骸技能时，获得1层【柔软的梦】，同名声骸只可触发一次，最多可叠加2层，持续10秒，叠加至2层后施放声骸技能不刷新持续时间。该效果10秒内最多生效1次，若切换至其他角色则该效果提前结束。
    第1层：普攻伤害加成提升40%；
    第2层：无视目标12%湮灭属性抗性。
    """

    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """造成普攻伤害"""
        if attr.char_damage == attack_damage:
            dmg = f"{self.param(6)}"
            title = self.get_title()
            msg = f"普攻伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

        if attr.role and attr.role.role.roleId == 1607:
            dmg = f"{self.param(8)}"
            title = self.get_title()
            msg = f"无视目标{dmg}%湮灭属性抗性"
            attr.add_enemy_resistance(-calc_percent_expression(dmg), title, msg)


class Weapon_21050064(WeaponAbstract):
    id = 21050064
    type = 5
    name = "异度"

    # 造成普攻或重击伤害时，治疗效果加成提升3%
    def cast_attack(self, attr: DamageAttribute, isGroup: bool = False):
        """造成普攻伤害"""
        if attr.char_damage != heal_bonus:
            return
        dmg = f"{self.param(0)}*{self.param(2)}"
        title = self.get_title()
        msg = f"造成普攻伤害时，治疗效果加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True

    def cast_hit(self, attr: DamageAttribute, isGroup: bool = False):
        """造成重击伤害"""
        if attr.char_damage != heal_bonus:
            return
        dmg = f"{self.param(0)}*{self.param(2)}"
        title = self.get_title()
        msg = f"造成重击伤害时，治疗效果加成提升{dmg}"
        attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21050066(WeaponAbstract):
    id = 21050066
    type = 5
    name = "幽冥的忘忧章"

    # 造成声骸技能伤害后12秒内，共鸣技能伤害加成提升32%，声骸技能伤害加深32%，且造成伤害时无视目标8%防御。
    def cast_phantom(self, attr: DamageAttribute, isGroup: bool = False):
        """造成声骸技能伤害"""
        # 无视目标8%防御
        dmg = f"{self.param(4)}"
        title = self.get_title()
        msg = f"造成声骸技能伤害后，无视目标{dmg}%防御"
        attr.add_defense_reduction(calc_percent_expression(dmg), title, msg)
        if attr.char_damage == phantom_damage:
            dmg = f"{self.param(3)}"
            title = self.get_title()
            msg = f"造成声骸技能伤害后，声骸技能伤害加深{dmg}"
            attr.add_dmg_deepen(calc_percent_expression(dmg), title, msg)

        if attr.char_damage == skill_damage:
            dmg = f"{self.param(2)}"
            title = self.get_title()
            msg = f"造成声骸技能伤害后，共鸣技能伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)


class Weapon_21050074(WeaponAbstract):
    id = 21050074
    type = 5
    name = "清音"

    # 施放共鸣解放时，自身攻击提升15%，持续15秒。
    def cast_liberation(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣解放"""
        if attr.char_template != temp_atk:
            return

        dmg = f"{self.param(0)}"
        title = self.get_title()
        msg = f"施放共鸣解放时，自身攻击提升{dmg}"
        attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21050084(WeaponAbstract):
    id = 21050084
    type = 5
    name = "核熔星盘"

    # 施放共鸣技能时，获得6点共鸣能量，且攻击提升10%，持续16秒。
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_template != temp_atk:
            return
        dmg = f"{self.param(1)}"
        title = self.get_title()
        msg = f"施放共鸣技能时，获得{self.param(0)}点共鸣能量，且攻击提升{dmg}"
        attr.add_atk_percent(calc_percent_expression(dmg), title, msg)
        return True


class Weapon_21050094(WeaponAbstract):
    id = 21050094
    type = 5
    name = "虚饰的华尔兹"

    # 对带有【异常效应】的怪物造成伤害时，自身攻击提升4%，持续10秒，每秒可触发1次，可叠加4层。
    def do_action(
        self,
        func_list: Union[List[str], str],
        attr: DamageAttribute,
        isGroup: bool = False,
    ):
        if attr.is_env_abnormal and attr.char_template == temp_atk:
            dmg = f"{self.param(0)}*{self.param(2)}"
            title = self.get_title()
            msg = f"对带有【异常效应】的怪物造成伤害时，自身攻击提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


class Weapon_21050104(WeaponAbstract):
    id = 21050104
    type = 5
    name = "曜光"

    # 施放共鸣技能时，攻击和普攻伤害加成提升9%
    def cast_skill(self, attr: DamageAttribute, isGroup: bool = False):
        """施放共鸣技能"""
        if attr.char_damage == attack_damage:
            dmg = f"{self.param(0)}"
            title = self.get_title()
            msg = f"施放共鸣技能时，普攻伤害加成提升{dmg}"
            attr.add_dmg_bonus(calc_percent_expression(dmg), title, msg)

        if attr.char_template == temp_atk:
            dmg = f"{self.param(0)}"
            title = self.get_title()
            msg = f"施放共鸣技能时，攻击加成提升{dmg}"
            attr.add_atk_percent(calc_percent_expression(dmg), title, msg)


def register_weapon():
    # 自动注册所有以 Weapon_ 开头的类
    for name, obj in globals().items():
        if name.startswith("Weapon_") and hasattr(obj, "id"):
            WavesWeaponRegister.register_class(obj.id, obj)
