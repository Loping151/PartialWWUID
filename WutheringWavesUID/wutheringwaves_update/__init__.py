from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from .draw_update_log import draw_update_log_img

sv_waves_update_history = SV("waves更新记录", pm=1)


@sv_waves_update_history.on_fullmatch(("更新记录", "更新日志"))
async def send_waves_update_log_msg(bot: Bot, ev: Event):
    im = await draw_update_log_img()
    await bot.send(im)
