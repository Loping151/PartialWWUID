import json
from typing import Dict, List

from gsuid_core.bot import msgjson

from ..utils.name_convert import (
    alias_to_char_name_list,
    alias_to_char_name_optional,
)
from ..utils.resource.RESOURCE_PATH import CUSTOM_CHAR_ALIAS_PATH


class CharAliasOps:
    def __init__(self):
        self.custom_data = None
        self.load_custom_data()

    def load_custom_data(self):
        with open(CUSTOM_CHAR_ALIAS_PATH, "r", encoding="UTF-8") as f:
            self.custom_data = msgjson.decode(f.read(), type=Dict[str, List[str]])

    def save_custom_data(self):
        with open(CUSTOM_CHAR_ALIAS_PATH, "w", encoding="UTF-8") as f:
            json.dump(self.custom_data, f, ensure_ascii=False, indent=2)

    def delete_char_alias(self, char_name: str, new_alias: str) -> str:
        if not self.custom_data:
            return "别名配置文件不存在，请检查文件路径"

        std_char_name = alias_to_char_name_optional(char_name)
        if not std_char_name:
            return f"角色【{char_name}】不存在，请检查名称"

        check_new_alias = alias_to_char_name_optional(new_alias)
        if not check_new_alias:
            return f"别名【{new_alias}】不存在，无法删除"

        if std_char_name not in self.custom_data:
            return f"角色【{char_name}】不存在别名文件内，请检查文件"

        if new_alias not in self.custom_data[std_char_name]:
            return f"别名【{new_alias}】不存在，无法删除"

        self.custom_data[std_char_name].remove(new_alias)
        self.save_custom_data()
        return f"成功为角色【{std_char_name}】删除别名【{new_alias}】"

    def add_char_alias(self, char_name: str, new_alias: str) -> str:
        if not self.custom_data:
            return "别名配置文件不存在，请检查文件路径"

        std_char_name = alias_to_char_name_optional(char_name)
        if not std_char_name:
            return f"角色【{char_name}】不存在，请检查名称"

        check_new_alias = alias_to_char_name_optional(new_alias)
        if check_new_alias:
            return f"别名【{new_alias}】已被角色【{check_new_alias}】占用"

        self.custom_data[std_char_name].append(new_alias)
        self.save_custom_data()
        return f"成功为角色【{char_name}】添加别名【{new_alias}】"


async def action_char_alias(action: str, char_name: str, new_alias: str) -> str:
    if not CUSTOM_CHAR_ALIAS_PATH.exists():
        return "别名配置文件不存在，请检查文件路径"

    cao = CharAliasOps()

    if action == "添加":
        return cao.add_char_alias(char_name, new_alias)
    elif action == "删除":
        return cao.delete_char_alias(char_name, new_alias)
    else:
        return "无效的操作，请检查操作"


async def char_alias_list(char_name: str):
    std_char_name = alias_to_char_name_optional(char_name)
    if not std_char_name:
        return f"角色【{char_name}】不存在，请检查名称"

    alias_list = alias_to_char_name_list(char_name)
    if not alias_list:
        return f"角色【{char_name}】不存在，请检查名称"

    res = [
        f"角色{std_char_name}别名列表：",
        *alias_list,
    ]

    return "\n".join(res)
