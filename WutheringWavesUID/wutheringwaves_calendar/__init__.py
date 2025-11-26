from typing import Any, List

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.button import WavesButton
from .draw_calendar_card import draw_calendar_img

sv_waves_calendar = SV("waves日历")


@sv_waves_calendar.on_fullmatch((f"个人日历", f"日历"), block=True)
async def send_waves_calendar_pic(bot: Bot, ev: Event):
    uid = ""
    im = await draw_calendar_img(ev, uid)
    if isinstance(im, str):
        return await bot.send(im)
    else:
        buttons: List[Any] = [
            WavesButton("深塔", "深塔"),
            WavesButton("冥海", "冥海"),
        ]
        return await bot.send_option(im, buttons)
