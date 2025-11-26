from typing import Any, List

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.button import WavesButton
from .draw_char_hold_rate import get_char_hold_rate_img
from .draw_slash_appear_rate import draw_slash_use_rate
from .draw_tower_appear_rate import draw_tower_use_rate

sv_char_hold_rate = SV("waves角色持有率")
sv_tower_appear_rate = SV("waves深塔出场率", priority=1)
sv_slash_appear_rate = SV("waves冥想出场率", priority=1)


# 角色持有率指令
@sv_char_hold_rate.on_command(
    (
        "角色持有率",
        "角色持有率列表",
        "持有率",
        "群角色持有率",
        "群角色持有率列表",
        "群持有率",
    )
)
async def handle_char_hold_rate(bot: Bot, ev: Event):
    if "群" in ev.command:
        if not ev.group_id:
            return await bot.send("请在群聊中使用")
        img = await get_char_hold_rate_img(ev, ev.group_id)
    else:
        img = await get_char_hold_rate_img(ev)
    buttons: List[Any] = [
        WavesButton("UP持有率", "角色持有率UP"),
        WavesButton("持有率", "角色持有率"),
        WavesButton("持有率4星", "角色持有率4"),
        WavesButton("持有率5星", "角色持有率5"),
        WavesButton("群持有率", "群角色持有率"),
    ]
    await bot.send_option(img, buttons)


# 深塔出场率指令
@sv_tower_appear_rate.on_command(
    (
        "深塔使用率",
        "深塔出场率",
        "深塔出场率列表",
        "出场率",
    ),
    block=True,
)
async def handle_tower_appear_rate(bot: Bot, ev: Event):
    img = await draw_tower_use_rate(ev)
    buttons: List[Any] = [
        WavesButton("深塔出场率", "深塔使用率"),
        WavesButton("左4出场率", "深塔出场率左"),
        WavesButton("右4出场率", "深塔出场率右"),
        WavesButton("中2出场率", "深塔出场率中"),
    ]
    await bot.send_option(img, buttons)


# 冥想出场率指令
@sv_slash_appear_rate.on_command(
    (
        "无尽总使用率",
        "无尽总出场率",
        "无尽总出场率列表",
        "无尽使用率",
        "无尽出场率",
        "无尽出场率列表",
        "冥海总使用率",
        "冥海总出场率",
        "冥海总出场率列表",
        "冥海使用率",
        "冥海出场率",
        "冥海出场率列表",
        "冥歌海墟总使用率",
        "冥歌海墟总出场率",
        "冥歌海墟总出场率列表",
        "冥歌海墟使用率",
        "冥歌海墟出场率",
        "冥歌海墟出场率列表",
    ),
    block=True,
)
async def handle_slash_appear_rate(bot: Bot, ev: Event):
    img = await draw_slash_use_rate(ev)
    buttons: List[Any] = [
        WavesButton("总出场率", "冥海出场率"),
        WavesButton("总使用率", "冥海总使用率"),
        WavesButton("上半出场率", "冥海出场率上半"),
        WavesButton("下半出场率", "冥海出场率下半"),
    ]
    await bot.send_option(img, buttons)
