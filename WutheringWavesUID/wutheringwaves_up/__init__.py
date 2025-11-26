from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..wutheringwaves_up.pool import get_pool_data_by_type

sv_pool_countdown = SV("鸣潮卡池倒计时")


@sv_pool_countdown.on_command(
    (
        "卡池倒计时",
        "未复刻统计",
        "未复刻角色",
        "未复刻角色统计",
        "未复刻武器",
        "未复刻武器统计",
    )
)
async def get_pool_countdown(bot: Bot, ev: Event):
    star = 5
    if ev.text.strip():
        text = ev.text.strip()
        if "4" in text or "四" in text:
            star = 4

    query_type = "角色"
    if "角色" in ev.command:
        query_type = "角色"
    elif "武器" in ev.command:
        query_type = "武器"

    msg = await get_pool_data_by_type(query_type, star)
    if msg:
        await bot.send(msg)
