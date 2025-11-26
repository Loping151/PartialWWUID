from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.at_help import ruser_id
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_103
from ..utils.hint import error_reply
from .draw_echo_list import get_draw_list

sv_waves_echo_list = SV(f"声骸展示")


@sv_waves_echo_list.on_fullmatch(
    (
        f"声骸列表",
        f"我的声骸",
        f"声骸仓库",
        f"声骸",
        f"声骇",
    )
)
async def send_echo_list_msg(bot: Bot, ev: Event):
    user_id = ruser_id(ev)
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))

    # 更新groupid
    await WavesBind.insert_waves_uid(
        user_id, ev.bot_id, uid, ev.group_id, lenth_limit=9
    )

    #
    im = await get_draw_list(ev, uid, user_id)
    return await bot.send(im)
