from ...utils.damage.abstract import EchoAbstract, WavesEchoRegister
from .damage import DamageAttribute
from .utils import (
    CHAR_ATTR_CELESTIAL,
    CHAR_ATTR_FREEZING,
    CHAR_ATTR_MOLTEN,
    CHAR_ATTR_SIERRA,
    CHAR_ATTR_SINKING,
    CHAR_ATTR_VOID,
    attack_damage,
    hit_damage,
    liberation_damage,
    skill_damage,
    temp_atk,
)


class Echo_390070051(EchoAbstract):
    id = 390070051
    name = "先锋幼岩"


class Echo_390070052(EchoAbstract):
    id = 390070052
    name = "裂变幼岩"


class Echo_390070053(EchoAbstract):
    id = 390070053
    name = "惊蛰猎手"


class Echo_390070064(EchoAbstract):
    id = 390070064
    name = "鸣泣战士"


class Echo_390070065(EchoAbstract):
    id = 390070065
    name = "审判战士"


class Echo_390070066(EchoAbstract):
    id = 390070066
    name = "咔嚓嚓"


class Echo_390070067(EchoAbstract):
    id = 390070067
    name = "阿嗞嗞"


class Echo_390070068(EchoAbstract):
    id = 390070068
    name = "呼咻咻"


class Echo_390070069(EchoAbstract):
    id = 390070069
    name = "呜咔咔"


class Echo_390070070(EchoAbstract):
    id = 390070070
    name = "破霜猎手"


class Echo_390070071(EchoAbstract):
    id = 390070071
    name = "巡徊猎手"


class Echo_390070074(EchoAbstract):
    id = 390070074
    name = "游弋蝶"


class Echo_390070075(EchoAbstract):
    id = 390070075
    name = "碎獠猪"


class Echo_390070076(EchoAbstract):
    id = 390070076
    name = "咕咕河豚"


class Echo_390070077(EchoAbstract):
    id = 390070077
    name = "遁地鼠"


class Echo_390070078(EchoAbstract):
    id = 390070078
    name = "绿熔蜥（稚形）"


class Echo_390070079(EchoAbstract):
    id = 390070079
    name = "刺玫菇（稚形）"


class Echo_390070100(EchoAbstract):
    id = 390070100
    name = "火鬃狼"


class Echo_390070105(EchoAbstract):
    id = 390070105
    name = "寒霜陆龟"


class Echo_390077004(EchoAbstract):
    id = 390077004
    name = "紫羽鹭"


class Echo_390077005(EchoAbstract):
    id = 390077005
    name = "青羽鹭"


class Echo_390077012(EchoAbstract):
    id = 390077012
    name = "热熔棱镜"


class Echo_390077013(EchoAbstract):
    id = 390077013
    name = "冷凝棱镜"


class Echo_390077016(EchoAbstract):
    id = 390077016
    name = "衍射棱镜"


class Echo_390077017(EchoAbstract):
    id = 390077017
    name = "湮灭棱镜"


class Echo_390077021(EchoAbstract):
    id = 390077021
    name = "坚岩斗士"


class Echo_390077022(EchoAbstract):
    id = 390077022
    name = "奏谕乐师"


class Echo_390077023(EchoAbstract):
    id = 390077023
    name = "振铎乐师"


class Echo_390077024(EchoAbstract):
    id = 390077024
    name = "磐石守卫"


class Echo_390077025(EchoAbstract):
    id = 390077025
    name = "冥渊守卫"


class Echo_390077028(EchoAbstract):
    id = 390077028
    name = "绿熔蜥"


class Echo_390077029(EchoAbstract):
    id = 390077029
    name = "刺玫菇"


class Echo_390077033(EchoAbstract):
    id = 390077033
    name = "暗鬃狼"


class Echo_390077038(EchoAbstract):
    id = 390077038
    name = "箭簇熊"


class Echo_390080003(EchoAbstract):
    id = 390080003
    name = "云闪之鳞"

    # 终结一击命中后，自身导电伤害加成提升12.00%，共鸣解放伤害加成提升12.00%，持续15秒。
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_VOID:
            title = self.name
            msg = "自身导电伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == liberation_damage:
            title = self.name
            msg = "共鸣解放伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_390080005(EchoAbstract):
    id = 390080005
    name = "鸣钟之龟"


class Echo_390080007(EchoAbstract):
    id = 390080007
    name = "燎照之骑"

    # 最后一段命中敌人后，自身热熔伤害加成提升12.00%，普攻伤害加成提升12.00%，持续15秒。

    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_MOLTEN:
            title = self.name
            msg = "自身热熔伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == attack_damage:
            title = self.name
            msg = "普攻伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_391070105(EchoAbstract):
    id = 391070105
    name = "异相·寒霜陆龟"


class Echo_391077024(EchoAbstract):
    id = 391077024
    name = "异相·磐石守卫"


class Echo_391080003(Echo_390080003):
    id = 391080003
    name = "异相·云闪之鳞"


class Echo_6000038(EchoAbstract):
    id = 6000038
    name = "幼猿"


class Echo_6000039(EchoAbstract):
    id = 6000039
    name = "朔雷之鳞"

    # 爪击命中后，自身导电伤害加成提升12.00%，重击伤害加成提升12.00%，持续15秒。
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_VOID:
            title = self.name
            msg = "自身导电伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == hit_damage:
            title = self.name
            msg = "重击伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_6000040(EchoAbstract):
    id = 6000040
    name = "戏猿"


class Echo_6000041(EchoAbstract):
    id = 6000041
    name = "晶螯蝎"


class Echo_6000042(EchoAbstract):
    id = 6000042
    name = "无冠者"

    # 幻形后，自身湮灭伤害加成提升12.00%，共鸣技能伤害加成提升12.00%，持续15秒。
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_SINKING:
            title = self.name
            msg = "自身湮灭伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == skill_damage:
            title = self.name
            msg = "共鸣技能伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_6000043(EchoAbstract):
    id = 6000043
    name = "飞廉之猩"

    # 追击命中后，自身气动伤害加成提升12.00%，重击伤害加成提升12.00%，持续15秒。
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_SIERRA:
            title = self.name
            msg = "气动伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == hit_damage:
            title = self.name
            msg = "重击伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_390180010(Echo_6000043):
    id = 390180010
    name = "异相·飞廉之猩"


class Echo_6000044(EchoAbstract):
    id = 6000044
    name = "辉萤军势"

    # 每次冲击使自身冷凝伤害加成提升4.00%，共鸣技能伤害加成提升4.00%，最多3层
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_FREEZING:
            title = self.name
            msg = "冷凝伤害加成提升4.00%*3"
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == skill_damage:
            title = self.name
            msg = "共鸣技能伤害加成提升4.00%*3"
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_6000045(EchoAbstract):
    id = 6000045
    name = "哀声鸷"

    # 自身衍射伤害加成提升12.00%，共鸣解放伤害加成提升12.00%
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_attr == CHAR_ATTR_CELESTIAL:
            title = self.name
            msg = "衍射伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)

        if attr.char_damage == liberation_damage:
            title = self.name
            msg = "共鸣解放伤害加成提升12.00%"
            attr.add_dmg_bonus(0.12, title, msg)


class Echo_6000046(EchoAbstract):
    id = 6000046
    name = "车刃镰"


class Echo_6000047(EchoAbstract):
    id = 6000047
    name = "啾啾河豚"


class Echo_6000048(EchoAbstract):
    id = 6000048
    name = "聚械机偶"

    # 施放声骸技能后，自身攻击提升12.00%
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_template == temp_atk:
            title = self.name
            msg = "自身攻击提升12.00%"
            attr.add_atk_percent(0.12, title, msg)


class Echo_6000049(EchoAbstract):
    id = 6000049
    name = "巡哨机傀"


class Echo_6000050(EchoAbstract):
    id = 6000050
    name = "通行灯偶"


class Echo_6000051(EchoAbstract):
    id = 6000051
    name = "叮咚咚"


class Echo_6000052(EchoAbstract):
    id = 6000052
    name = "无常凶鹭"


class Echo_6000053(EchoAbstract):
    id = 6000053
    name = "无妄者"


class Echo_6000054(EchoAbstract):
    id = 6000054
    name = "融火虫"


class Echo_6000055(EchoAbstract):
    id = 6000055
    name = "侏侏鸵"


class Echo_6000056(EchoAbstract):
    id = 6000056
    name = "雪鬃狼"


class Echo_6000057(EchoAbstract):
    id = 6000057
    name = "游鳞机枢"


class Echo_6000058(EchoAbstract):
    id = 6000058
    name = "踏光兽"


class Echo_6000059(EchoAbstract):
    id = 6000059
    name = "角"

    # 自身的共鸣技能伤害加成提升16.00%
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_damage == skill_damage:
            title = self.name
            msg = "共鸣技能伤害加成提升16.00%"
            attr.add_dmg_bonus(0.16, title, msg)


class Echo_6000060(EchoAbstract):
    id = 6000060
    name = "无归的谬误"

    # 自身共鸣效率提升10%，全队角色攻击提升10%
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.char_template == temp_atk:
            title = self.name
            msg = "全队角色攻击提升10%"
            attr.add_atk_percent(0.1, title, msg)


class Echo_6000061(EchoAbstract):
    id = 6000061
    name = "风鬃狼"


class Echo_6000062(EchoAbstract):
    id = 6000062
    name = "雷鬃狼"


class Echo_6000063(EchoAbstract):
    id = 6000063
    name = "霜鬃狼"


class Echo_6000064(EchoAbstract):
    id = 6000064
    name = "浮灵偶·海德"


class Echo_6000065(EchoAbstract):
    id = 6000065
    name = "浮灵偶·蕾弗"


class Echo_6000066(EchoAbstract):
    id = 6000066
    name = "浮灵偶·莱特"


class Echo_6000067(EchoAbstract):
    id = 6000067
    name = "幽翎火"


class Echo_6000068(EchoAbstract):
    id = 6000068
    name = "云海妖精"


class Echo_6000069(EchoAbstract):
    id = 6000069
    name = "魔术先生"


class Echo_6000070(EchoAbstract):
    id = 6000070
    name = "寂寞小姐"


class Echo_6000071(EchoAbstract):
    id = 6000071
    name = "工头布偶"


class Echo_6000072(EchoAbstract):
    id = 6000072
    name = "欺诈奇藏"


class Echo_6000073(EchoAbstract):
    id = 6000073
    name = "巡游骑士"


class Echo_6000074(EchoAbstract):
    id = 6000074
    name = "幻昼骑士"


class Echo_6000075(EchoAbstract):
    id = 6000075
    name = "暗夜骑士"


class Echo_6000076(EchoAbstract):
    id = 6000076
    name = "毒冠贵族"

    # 首位装备该声骸技能时，自身冷凝伤害加成提升12.00%
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"冷凝伤害加成": "12%"}


class Echo_6000077(EchoAbstract):
    id = 6000077
    name = "持刃贵族"


class Echo_6000078(EchoAbstract):
    id = 6000078
    name = "凝水贵族"


class Echo_6000079(EchoAbstract):
    id = 6000079
    name = "浮灵偶"


class Echo_6000080(EchoAbstract):
    id = 6000080
    name = "琉璃刀伶"

    # 在首位装备该声骸技能时，自身导电伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"导电伤害加成": "12%"}


class Echo_6000081(EchoAbstract):
    id = 6000081
    name = "巨布偶"


class Echo_6000082(EchoAbstract):
    id = 6000082
    name = "罗蕾莱"

    # 在首位装配该声骸技能时，自身湮灭伤害加成提升12.00%，普攻伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"湮灭伤害加成": "12%", "普攻伤害加成": "12%"}


class Echo_6000083(EchoAbstract):
    id = 6000083
    name = "异构武装"

    # 在首位装配该声骸技能时，自身获得12.00%冷凝伤害加成提升，12.00%共鸣技能伤害加成提升
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"共鸣技能伤害加成": "12%", "冷凝伤害加成": "12%"}


class Echo_6000084(EchoAbstract):
    id = 6000084
    name = "叹息古龙"

    # 在首位装配该声骸技能时，自身获得12.00%热熔伤害加成提升，12.00%普攻伤害加成提升
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"热熔伤害加成": "12%", "普攻伤害加成": "12%"}


class Echo_6000085(EchoAbstract):
    id = 6000085
    name = "赫卡忒"

    # 在首位装配该声骸技能时，自身协同攻击造成的伤害提升40.00%。
    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.sync_strike:
            title = self.name
            msg = "自身协同攻击造成的伤害提升40.00%"
            attr.add_dmg_bonus(0.4, title, msg)


class Echo_6000086(EchoAbstract):
    id = 6000086
    name = "梦魇·飞廉之猩"

    # 在首位装配该声骸技能时，自身气动伤害加成提升12.00%，重击伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"气动伤害加成": "12%", "重击伤害加成": "12%"}


class Echo_6000087(EchoAbstract):
    id = 6000087
    name = "梦魇·无常凶鹭"

    # 在首位装配该声骸技能时，自身湮灭伤害加成提升12.00%，重击伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"湮灭伤害加成": "12%", "重击伤害加成": "12%"}


class Echo_6000088(EchoAbstract):
    id = 6000088
    name = "梦魇·云闪之鳞"

    # 在首位装配该声骸技能时，自身导电伤害加成提升12.00%，共鸣解放伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"导电伤害加成": "12%", "共鸣解放伤害加成": "12%"}


class Echo_6000089(EchoAbstract):
    id = 6000089
    name = "梦魇·朔雷之鳞"

    # 在首位装配该声骸技能时，自身导电伤害加成提升12.00%，共鸣技能伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"导电伤害加成": "12%", "共鸣技能伤害加成": "12%"}


class Echo_6000090(EchoAbstract):
    id = 6000090
    name = "梦魇·无冠者"

    # 在首位装配该声骸技能时，自身湮灭伤害加成提升12.00%，普攻伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"湮灭伤害加成": "12%", "普攻伤害加成": "12%"}


class Echo_6000091(EchoAbstract):
    id = 6000091
    name = "梦魇·燎照之骑"

    # 在首位装配该声骸技能时，自身热熔伤害加成提升12.00%，共鸣技能伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"热熔伤害加成": "12%", "共鸣技能伤害加成": "12%"}


class Echo_6000092(EchoAbstract):
    id = 6000092
    name = "梦魇·哀声鸷"

    # 在首位装配该声骸技能时，自身衍射伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"衍射伤害加成": "12%"}


class Echo_6000093(EchoAbstract):
    id = 6000093
    name = "愚金幼岩"


class Echo_6000094(EchoAbstract):
    id = 6000094
    name = "釉变幼岩"


class Echo_6000095(EchoAbstract):
    id = 6000095
    name = "气动棱镜"


class Echo_6000096(EchoAbstract):
    id = 6000096
    name = "重塑雕像的拳砾"


class Echo_6000097(EchoAbstract):
    id = 6000097
    name = "飓力熊"


class Echo_6000098(EchoAbstract):
    id = 6000098
    name = "卫冕节使"


class Echo_6000099(EchoAbstract):
    id = 6000099
    name = "赦罪节使"


class Echo_6000100(EchoAbstract):
    id = 6000100
    name = "慈悲节使"


class Echo_6000101(EchoAbstract):
    id = 6000101
    name = "小翼龙·气动"


class Echo_6000102(EchoAbstract):
    id = 6000102
    name = "小翼龙·导电"


class Echo_6000103(EchoAbstract):
    id = 6000103
    name = "小翼龙·冷凝"


class Echo_6000104(EchoAbstract):
    id = 6000104
    name = "荣光节使"

    # 在首位装配该声骸技能时，自身衍射伤害加成提升12.00%，重击伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"衍射伤害加成": "12%", "重击伤害加成": "12%"}


class Echo_6000105(EchoAbstract):
    id = 6000105
    name = "梦魇·辉萤军势"

    # 在首位装配该声骸技能时，自身冷凝伤害加成提升12.00%，协同攻击造成的伤害提升30.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"冷凝伤害加成": "12%"}

    def damage(self, attr: DamageAttribute, isGroup: bool = False):
        if attr.sync_strike:
            title = self.name
            msg = "自身协同攻击造成的伤害提升30.00%"
            attr.add_dmg_bonus(0.3, title, msg)


class Echo_6000106(EchoAbstract):
    id = 6000106
    name = "共鸣回响·芙露德莉斯"

    # 在首位装配该声骸技能时，自身气动伤害加成提升10.00%，当装配角色为漂泊者·气动或卡提希娅时，自身气动伤害加成额外提升10.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        res = {"气动伤害加成": "10%"}
        if role_id in [1406, 1408, 1409]:
            res["气动伤害加成"] = "20%"
        return res


class Echo_6000107(EchoAbstract):
    id = 6000107
    name = "小翼龙·热熔"


class Echo_6000108(EchoAbstract):
    id = 6000108
    name = "小翼龙·衍射"


class Echo_6000109(EchoAbstract):
    id = 6000109
    name = "小翼龙·湮灭"


class Echo_6000110(EchoAbstract):
    id = 6000110
    name = "苦信者的作俑"


class Echo_6000111(EchoAbstract):
    id = 6000111
    name = "传道者的遗形"


class Echo_6000112(EchoAbstract):
    id = 6000112
    name = "角鳄"

    # 首位装配该声骸技能时，自身气动伤害加成提升12.00%，共鸣解放伤害加成提升12.00%
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"气动伤害加成": "12%", "共鸣解放伤害加成": "12%"}


class Echo_6000113(EchoAbstract):
    id = 6000113
    name = "梦魇·凯尔匹"

    # 在首位装配该声骸技能时，自身冷凝伤害加成提升12.00%，气动伤害加成提升12.00%
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"冷凝伤害加成": "12%", "气动伤害加成": "12%"}


class Echo_6000114(EchoAbstract):
    id = 6000114
    name = "荣耀狮像"

    # 在首位装配该声骸技能时，自身热熔伤害加成提升12.00%，共鸣解放伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"热熔伤害加成": "12%", "共鸣解放伤害加成": "12%"}


class Echo_6000115(EchoAbstract):
    id = 6000115
    name = "梦魇·赫卡忒"

    # 在首位装配该声骸技能时，自身湮灭伤害加成提升12.00%，声骸技能伤害加成提升20.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"湮灭伤害加成": "12%", "声骸技能伤害加成": "20%"}


class Echo_6000116(EchoAbstract):
    id = 6000116
    name = "共鸣回响·芬莱克"

    # 在首位装配该声骸技能时，自身气动伤害加成提升12.00%，重击伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"气动伤害加成": "12%", "重击伤害加成": "12%"}


class Echo_6000117(EchoAbstract):
    id = 6000117
    name = "梦魇·审判战士"


class Echo_6000118(EchoAbstract):
    id = 6000118
    name = "梦魇·破霜猎手"


class Echo_6000119(EchoAbstract):
    id = 6000119
    name = "梦魇·振铎乐师"


class Echo_6000120(EchoAbstract):
    id = 6000120
    name = "蚀脊龙"

    # 在首位装配该声骸技能时，自身热熔伤害加成提升12.00%，声骸技能伤害加成提升20.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"热熔伤害加成": "12%", "声骸技能伤害加成": "20%"}


class Echo_6000121(EchoAbstract):
    id = 6000121
    name = "伪作的神王"

    # 在首位装配该声骸技能时，自身导电伤害加成提升12.00%，重击伤害加成提升12.00%
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"导电伤害加成": "12%", "重击伤害加成": "12%"}


class Echo_6000160(EchoAbstract):
    id = 6000160
    name = "海之女"

    # 在首位装配该声骸技能时，自身气动伤害加成提升12.00%，共鸣解放伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"气动伤害加成": "12%", "共鸣解放伤害加成": "12%"}


class Echo_6000161(EchoAbstract):
    id = 6000161
    name = "梦魇·紫羽鹭"


class Echo_6000162(EchoAbstract):
    id = 6000162
    name = "梦魇·青羽鹭"


class Echo_6000163(EchoAbstract):
    id = 6000163
    name = "梦魇·惊蛰猎手"


class Echo_6000164(EchoAbstract):
    id = 6000164
    name = "梦魇·巡徊猎手"


class Echo_6000165(EchoAbstract):
    id = 6000165
    name = "梦魇·咕咕河豚"


class Echo_6000166(EchoAbstract):
    id = 6000166
    name = "梦魇·啾啾河豚"


class Echo_6000167(EchoAbstract):
    id = 6000167
    name = "共鸣回响·鸣式·利维亚坦"

    # 在首位装配该声骸技能时，自身湮灭伤害加成提升12.00%，共鸣解放伤害加成提升12.00%。
    def do_equipment_first(self, role_id: int):
        """首位装备"""
        return {"湮灭伤害加成": "12%", "共鸣解放伤害加成": "12%"}


class Echo_6000168(EchoAbstract):
    id = 6000168
    name = "梦魇·绿熔蜥"


class Echo_6000169(EchoAbstract):
    id = 6000169
    name = "梦魇·绿熔蜥（稚形）"


class Echo_6000170(EchoAbstract):
    id = 6000170
    name = "梦魇·刺玫菇（稚形）"


def register_echo():
    # 自动注册所有以 Echo_ 开头的类
    for name, obj in globals().items():
        if name.startswith("Echo_") and hasattr(obj, "id"):
            WavesEchoRegister.register_class(obj.id, obj)
