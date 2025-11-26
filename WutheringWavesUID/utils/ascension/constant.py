from typing import Union

fixed_name = [
    "暴击提升",
    "暴击伤害提升",
    "生命提升",
    "防御提升",
    "攻击提升",
    "共鸣效率提升",
    "治疗效果加成提升",
    "冷凝伤害加成提升",
    "衍射伤害加成提升",
    "导电伤害加成提升",
    "热熔伤害加成提升",
    "气动伤害加成提升",
    "湮灭伤害加成提升",
    "全属性伤害加成提升",
    "普攻伤害加成提升",
    "重击伤害加成提升",
    "共鸣技能伤害加成提升共鸣解放伤害加成提升",
]


def sum_percentages(*args):
    total = 0.0
    for percent in args:
        try:
            # 去除百分号并转换为浮点数
            num = float(percent.rstrip("%"))
            total += num
        except ValueError:
            return f"输入的百分比格式不正确: '{percent}'"

    return f"{total:.1f}%"


def sum_numbers(*args):
    total = 0.0
    for arg in args:
        try:
            num = float(arg)
            total += num
        except ValueError:
            return f"输入的字符串 '{arg}' 必须是可转换为数字的形式"
    return f"{total}"


def percent_to_float(value: Union[str, float]) -> float:
    if isinstance(value, str):
        return float(value.rstrip("%")) * 0.01
    return value
