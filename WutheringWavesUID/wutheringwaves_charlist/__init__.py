import re

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.at_help import ruser_id
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_103
from ..utils.hint import error_reply
from .draw_char_list import draw_char_list_img

sv_waves_char_list = SV("ww角色练度统计")


@sv_waves_char_list.on_regex(
    r"^(\d+)?(练度|练度统计|角色列表|刷新练度|刷新练度统计|刷新角色列表)$",
    block=True,
)
async def send_char_list_msg_new(bot: Bot, ev: Event):
    match = re.search(
        r"(?P<waves_id>\d+)?(?P<query_type>练度|练度统计|角色列表|刷新练度|刷新练度统计|刷新角色列表)",
        ev.raw_text,
    )
    if not match:
        return
    query_waves_id = match.group("waves_id")
    query_type = match.group("query_type")

    is_refresh = False
    if "刷新" in query_type:
        is_refresh = True

    is_peek = False
    if query_waves_id:
        is_peek = True
        if not query_waves_id.isdigit() or len(query_waves_id) != 9:
            return await bot.send("请输入正确的查询特征码")

    user_id = ruser_id(ev)
    user_waves_id = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not query_waves_id:
        query_waves_id = user_waves_id

    # 参数校验
    if not query_waves_id:
        return await bot.send(error_reply(WAVES_CODE_103))

    if not is_peek:
        # 更新groupid
        await WavesBind.insert_waves_uid(
            user_id, ev.bot_id, query_waves_id, ev.group_id, lenth_limit=9
        )

    im = await draw_char_list_img(
        query_waves_id,
        ev,
        user_id,
        is_refresh,
        is_peek,
        user_waves_id,
    )
    return await bot.send(im)
