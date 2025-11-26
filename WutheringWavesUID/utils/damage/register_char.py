from ...utils.damage.abstract import (
    CharAbstract,
    WavesCharRegister,
    WavesWeaponRegister,
)
from .damage import DamageAttribute
from .utils import (
    CHAR_ATTR_CELESTIAL,
    CHAR_ATTR_FREEZING,
    CHAR_ATTR_MOLTEN,
    CHAR_ATTR_SIERRA,
    CHAR_ATTR_SINKING,
    CHAR_ATTR_VOID,
    attack_damage,
    cast_variation,
    hit_damage,
    liberation_damage,
    skill_damage,
    temp_atk,
)


class Char_1102(CharAbstract):
    id = 1102
    name = "散华"
    starLevel = 4

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        if attr.char_template == temp_atk:
            if chain >= 6:
                title = "散华-六链"
                msg = "队伍中的角色攻击提升20%"
                attr.add_atk_percent(0.2, title, msg)

            title = "散华-合鸣效果-轻云出月"
            msg = "下一个登场的共鸣者攻击提升22.5%"
            attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = "散华-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        if attack_damage == attr.char_damage:
            title = "散华-延奏技能"
            msg = "下一位登场角色普攻伤害加深38%"
            attr.add_dmg_deepen(0.38, title, msg)


class Char_1103(CharAbstract):
    id = 1103
    name = "白芷"
    starLevel = 4


class Char_1104(CharAbstract):
    id = 1104
    name = "凌阳"
    starLevel = 5


class Char_1105(CharAbstract):
    id = 1105
    name = "折枝"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        if attr.char_template == temp_atk:
            if chain >= 4:
                title = f"{self.name}-四链"
                msg = "折枝施放共鸣解放虚实境趣时，队伍中角色攻击提升20%"
                attr.add_atk_percent(0.2, title, msg)

            title = f"{self.name}-合鸣效果-轻云出月"
            msg = "使用延奏技能后，下一个登场的共鸣者攻击提升22.5%"
            attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = f"{self.name}-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_attr == CHAR_ATTR_FREEZING:
            title = f"{self.name}-延奏技能"
            msg = "下一位登场角色冷凝伤害加深20%"
            attr.add_dmg_bonus(0.2, title, msg)

        if skill_damage == attr.char_damage:
            title = f"{self.name}-延奏技能"
            msg = "下一位登场角色共鸣技能伤害加深25%"
            attr.add_dmg_deepen(0.25, title, msg)


class Char_1106(CharAbstract):
    id = 1106
    name = "釉瑚"
    starLevel = 4


class Char_1107(CharAbstract):
    id = 1107
    name = "珂莱塔"
    starLevel = 5


class Char_1202(CharAbstract):
    id = 1202
    name = "炽霞"
    starLevel = 4


class Char_1203(CharAbstract):
    id = 1203
    name = "安可"
    starLevel = 5


class Char_1204(CharAbstract):
    id = 1204
    name = "莫特斐"
    starLevel = 4

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        if attr.char_template == temp_atk:
            if chain >= 6:
                title = "莫特斐-六链"
                msg = "施放共鸣解放暴烈终曲时，队伍中的角色攻击提升20%"
                attr.add_atk_percent(0.2, title, msg)

            title = "莫特斐-合鸣效果-轻云出月"
            msg = "使用延奏技能后，下一个登场的共鸣者攻击提升22.5%"
            attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = "莫特斐-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        if hit_damage == attr.char_damage:
            title = "莫特斐-延奏技能"
            msg = "下一位登场角色重击伤害加深38%"
            attr.add_dmg_deepen(0.38, title, msg)

        # 停驻之烟
        weapon_id = 21030015
        weapon_clz = WavesWeaponRegister.find_class(weapon_id)
        if weapon_clz:
            w = weapon_clz(weapon_id, 90, 6, resonLevel)
            w.do_action("buff", attr, isGroup)


class Char_1205(CharAbstract):
    id = 1205
    name = "长离"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        if attr.char_template == temp_atk:
            if chain >= 4:
                title = "长离-四链"
                msg = "施放变奏技能后，队伍中的角色攻击提升20%"
                attr.add_atk_percent(0.2, title, msg)

        if attr.char_attr == CHAR_ATTR_MOLTEN:
            title = "长离-延奏技能"
            msg = "下一位登场角色热熔伤害加深20%"
            attr.add_dmg_deepen(0.2, title, msg)

        if liberation_damage == attr.char_damage:
            title = "长离-延奏技能"
            msg = "下一位登场角色共鸣解放伤害加深25%"
            attr.add_dmg_deepen(0.25, title, msg)


class Char_1206(CharAbstract):
    id = 1206
    name = "布兰特"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        # 下一位登场角色热熔伤害加深20%，共鸣技能伤害加深25%
        if attr.char_attr == CHAR_ATTR_MOLTEN:
            title = "布兰特-延奏技能"
            msg = "下一位登场角色热熔伤害加深20%"
            attr.add_dmg_deepen(0.2, title, msg)

        if skill_damage == attr.char_damage:
            title = "布兰特-延奏技能"
            msg = "下一位登场角色共鸣解放伤害加深25%"
            attr.add_dmg_deepen(0.25, title, msg)


class Char_1301(CharAbstract):
    id = 1301
    name = "卡卡罗"
    starLevel = 5


class Char_1302(CharAbstract):
    id = 1302
    name = "吟霖"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        if attr.char_template == temp_atk:
            if chain >= 4:
                title = "吟霖-四链"
                msg = "共鸣回路审判之雷命中时，队伍中的角色攻击提升20%"
                attr.add_atk_percent(0.2, title, msg)

            title = "吟霖-合鸣效果-轻云出月"
            msg = "使用延奏技能后，下一个登场的共鸣者攻击提升22.5%"
            attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = "吟霖-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        # 下一位登场角色导电伤害加深20%，共鸣解放伤害加深25%
        if attr.char_attr == CHAR_ATTR_VOID:
            title = "吟霖-延奏技能"
            msg = "下一位登场角色导电伤害加深20%"
            attr.add_dmg_deepen(0.2, title, msg)

        if liberation_damage == attr.char_damage:
            title = "吟霖-延奏技能"
            msg = "下一位登场角色共鸣解放伤害加深25%"
            attr.add_dmg_deepen(0.25, title, msg)


class Char_1303(CharAbstract):
    id = 1303
    name = "渊武"
    starLevel = 4


class Char_1304(CharAbstract):
    id = 1304
    name = "今汐"
    starLevel = 5


class Char_1305(CharAbstract):
    id = 1305
    name = "相里要"
    starLevel = 5


class Char_1402(CharAbstract):
    id = 1402
    name = "秧秧"
    starLevel = 4


class Char_1403(CharAbstract):
    id = 1403
    name = "秋水"
    starLevel = 4


class Char_1404(CharAbstract):
    id = 1404
    name = "忌炎"
    starLevel = 5


class Char_1405(CharAbstract):
    id = 1405
    name = "鉴心"
    starLevel = 5


class Char_1406(CharAbstract):
    id = 1406
    name = "漂泊者·气动"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):

        if attr.char_attr == CHAR_ATTR_SIERRA:
            #  血誓盟约
            title = "风主-血誓盟约"
            msg = "风主施放共鸣技能时，附近队伍中登场角色气动伤害加深10%"
            attr.add_dmg_deepen(0.1, title, msg)

            # 流云逝尽之空
            # 角色为敌人添加【风蚀效应】时，队伍中角色气动伤害提升15%
            title = "风主-流云逝尽之空"
            msg = "队伍中的角色气动伤害提升15%"
            attr.add_dmg_bonus(0.15, title, msg)


class Char_1407(CharAbstract):
    id = 1407
    name = "夏空"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        pass


class Char_1408(Char_1406):
    id = 1408
    name = "漂泊者·气动"
    starLevel = 5


class Char_1501(CharAbstract):
    id = 1501
    name = "漂泊者·衍射"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        attr.set_env_spectro()
        title = "光主"
        msg = "触发光噪效应"
        attr.add_effect(title, msg)
        if chain >= 6:
            title = "光主-六链"
            msg = "施放共鸣技能时，目标衍射伤害抗性降低10%"
            attr.add_enemy_resistance(-0.1, title, msg)

        if attr.char_template == temp_atk:
            title = "光主-合鸣效果-轻云出月"
            msg = "下一个登场的共鸣者攻击提升22.5%"
            attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = "光主-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)


class Char_1502(Char_1501):
    id = 1502
    name = "漂泊者·衍射"
    starLevel = 5


class Char_1503(CharAbstract):
    id = 1503
    name = "维里奈"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        if attr.char_template == temp_atk:
            title = "维里奈-固有技能-自然的献礼"
            msg = "队伍中的角色攻击提升20%"
            attr.add_atk_percent(0.2, title, msg)

        if chain >= 4 and attr.char_attr == CHAR_ATTR_CELESTIAL:
            title = "维里奈-四链"
            msg = "队伍中的角色衍射伤害加成提升15%"
            attr.add_dmg_bonus(0.4, title, msg)

        if attr.char_template == temp_atk:
            title = "维里奈-合鸣效果-隐世回光"
            msg = "全队共鸣者攻击提升15%"
            attr.add_atk_percent(0.15, title, msg)

        title = "维里奈-声骸技能-鸣钟之龟"
        msg = "全队角色10.00%的伤害提升"
        attr.add_dmg_bonus(0.1, title, msg)

        title = "维里奈-延奏技能"
        msg = "队伍中的角色全伤害加深15%"
        attr.add_dmg_deepen(0.15, title, msg)


class Char_1504(CharAbstract):
    id = 1504
    name = "灯灯"
    starLevel = 4

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        if attr.char_template == temp_atk:
            if chain >= 6:
                title = f"{self.name}-六链"
                msg = "施放共鸣解放时，队伍中的角色的攻击提升20%"
                attr.add_atk_percent(0.2, title, msg)

            title = f"{self.name}-合鸣效果-轻云出月"
            msg = "使用延奏技能后，下一个登场的共鸣者攻击提升22.5%"
            attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = f"{self.name}-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        if skill_damage == attr.char_damage:
            title = f"{self.name}-延奏技能"
            msg = "下一位登场角色共鸣技能伤害加深38%"
            attr.add_dmg_deepen(0.38, title, msg)


class Char_1505(CharAbstract):
    id = 1505
    name = "守岸人"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        if attr.char_template == temp_atk:
            if chain >= 2:
                title = "守岸人-二链"
                msg = "队伍中的角色攻击提升40%"
                attr.add_atk_percent(0.4, title, msg)

            title = "守岸人-合鸣效果-隐世回光"
            msg = "全队共鸣者攻击提升15%"
            attr.add_atk_percent(0.15, title, msg)

        # 星序协响
        weapon_clz = WavesWeaponRegister.find_class(21050036)
        if weapon_clz:
            w = weapon_clz(21050036, 90, 6, resonLevel)
            w.do_action("skill_create_healing", attr, isGroup)

        if attr.char_template == temp_atk:
            title = "守岸人-声骸技能-无归的谬误"
            msg = "全队角色攻击提升10%"
            attr.add_atk_percent(0.1, title, msg)

        title = "守岸人-共鸣解放"
        msg = "暴击提升12.5%+暴击伤害提升25%"
        attr.add_crit_rate(0.125)
        attr.add_crit_dmg(0.25)
        attr.add_effect(title, msg)

        title = "守岸人-延奏技能"
        msg = "队伍中的角色全伤害加深15%"
        attr.add_dmg_deepen(0.15, title, msg)


class Char_1506(CharAbstract):
    id = 1506
    name = "菲比"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        attr.set_env_spectro()
        title = "菲比"
        msg = "触发光噪效应"
        attr.add_effect(title, msg)

        if attr.char_attr == CHAR_ATTR_CELESTIAL:
            title = "菲比-延奏技能-告解"
            msg = "使一定范围内的目标衍射伤害抗性减少10%"
            attr.add_enemy_resistance(-0.1, title, msg)

        if attr.char_template == temp_atk:
            title = f"{self.name}-合鸣效果-轻云出月"
            msg = "使用延奏技能后，下一个登场的共鸣者攻击提升22.5%"
            attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = f"{self.name}-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        if attr.env_spectro_deepen:
            title = f"{self.name}-延奏技能-告解"
            msg = "下一个变奏登场角色【光噪效应】伤害加深100%。"
            attr.add_dmg_deepen(1, title, msg)

            if chain >= 2:
                title = f"{self.name}-二链"
                msg = "告解状态下，默祷的【光噪效应】伤害加深效果额外提升120%。"
                attr.add_dmg_deepen(1.2, title, msg)

            if chain >= 4:
                title = f"{self.name}-四链"
                msg = "目标衍射伤害抗性降低10%，持续30秒"
                attr.add_enemy_resistance(-0.1, title, msg)

        # 和光回唱
        weapon_clz = WavesWeaponRegister.find_class(21050046)
        if weapon_clz:
            w = weapon_clz(21050046, 90, 6, resonLevel)
            method = getattr(w, "cast_extension", None)
            if callable(method):
                method(attr, isGroup)


class Char_1507(CharAbstract):
    id = 1507
    name = "赞妮"
    starLevel = 5


class Char_1508(CharAbstract):
    id = 1508
    name = "千咲"
    starLevel = 5

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        attr.set_env_havoc_bane()

        title = "千咲-共鸣回路-虚湮之线"
        msg = "对拥有虚无绞痕的目标造成伤害时，可无视其18%防御"
        attr.add_defense_reduction(0.18, title, msg)

        # 异常效应层数上限增加3层
        title = "千咲-延奏技能-解弦式第零定律"
        msg = "使目标层数上限增加3层"
        attr.add_effect(title, msg)
        # 注：这个记得单独写，是几层就是几层

        # 二链效果
        if chain >= 2:
            if attr.char_attr == CHAR_ATTR_SINKING:
                title = "千咲-二链"
                msg = "无视目标10%湮灭伤害抗性"
                attr.add_enemy_resistance(-0.1, title, msg)

            title = "千咲-二链"
            msg = "队伍中的角色处于虚湮之线状态时，全属性伤害加成提升50%"
            attr.add_dmg_bonus(0.5, title, msg)

        # 六链效果：异常效应伤害加深
        if attr.env_abnormal_deepen:
            title = "千咲-六链"
            msg = "拥有虚无绞痕·终焉的目标受到异常效应伤害加深30%"
            attr.add_dmg_deepen(0.3, title, msg)

        weapon_clz = WavesWeaponRegister.find_class(21010056)
        if weapon_clz:
            w = weapon_clz(21010056, 90, 6, resonLevel)
            method = getattr(w, "do_action", None)
            if callable(method):
                method([cast_variation], attr, isGroup)
            
class Char_1601(CharAbstract):
    id = 1601
    name = "桃祈"
    starLevel = 4


class Char_1602(CharAbstract):
    id = 1602
    name = "丹瑾"
    starLevel = 4

    # 下一位登场角色湮灭伤害加深23%，效果持续14秒，若切换至其他角色则该效果提前结束。

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        if CHAR_ATTR_SINKING == attr.char_attr:
            title = "丹瑾-延奏技能"
            msg = "下一位登场角色湮灭伤害加深23%"
            attr.add_dmg_deepen(0.23, title, msg)

            # 幽夜隐匿之帷
            title = "丹瑾-合鸣效果-幽夜隐匿之帷"
            msg = "下一位登场角色湮灭伤害加成提升15%"
            attr.add_dmg_bonus(0.15, title, msg)


class Char_1603(CharAbstract):
    id = 1603
    name = "椿"
    starLevel = 5


class Char_1604(CharAbstract):
    id = 1604
    name = "漂泊者·湮灭"
    starLevel = 5


class Char_1605(CharAbstract):
    id = 1605
    name = "漂泊者·湮灭"
    starLevel = 5


class Char_1606(CharAbstract):
    id = 1606
    name = "洛可可"
    starLevel = 5

    # 下一位登场角色湮灭伤害加深20%，普攻伤害加深25%，效果持续14秒，若切换至其他角色则该效果提前结束。

    def _do_buff(
        self,
        attr: DamageAttribute,
        chain: int = 0,
        resonLevel: int = 1,
        isGroup: bool = True,
    ):
        """获得buff"""
        if attr.char_template == temp_atk:
            title = "洛可可-共鸣解放"
            msg = "施放共鸣解放最多提供200点攻击"
            attr.add_atk_flat(200, title, msg)

            title = "洛可可-合鸣效果-轻云出月"
            msg = "下一个登场的共鸣者攻击提升22.5%"
            attr.add_atk_percent(0.225, title, msg)

        # 无常凶鹭
        title = "洛可可-声骸技能-无常凶鹭"
        msg = "施放延奏技能，则可使下一个变奏登场的角色伤害提升12%"
        attr.add_dmg_bonus(0.12, title, msg)

        if attack_damage == attr.char_damage:
            title = "洛可可-延奏技能"
            msg = "下一位登场角色普攻伤害加深25%"
            attr.add_dmg_deepen(0.25, title, msg)

        if CHAR_ATTR_SINKING == attr.char_attr:
            # # 幽夜隐匿之帷
            # title = "洛可可-合鸣效果-幽夜隐匿之帷"
            # msg = "下一个登场角色湮灭属性伤害加成提升15%"
            # attr.add_dmg_bonus(0.15, title, msg)

            title = "洛可可-延奏技能"
            msg = "下一位登场角色湮灭伤害加深20%"
            attr.add_dmg_deepen(0.2, title, msg)

            if chain >= 2:
                # 施放普攻幻想照进现实时，队伍中的角色湮灭伤害加成提升10%，可叠加3层
                title = "洛可可-二链"
                msg = "队伍中的角色湮灭伤害提升10%*4"
                attr.add_dmg_bonus(0.1 * 4, title, msg)


def register_char():
    # 自动注册所有以 Char_ 开头的类
    for name, obj in globals().items():
        if name.startswith("Char_") and hasattr(obj, "id"):
            WavesCharRegister.register_class(obj.id, obj)
