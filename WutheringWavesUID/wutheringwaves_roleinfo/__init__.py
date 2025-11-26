from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.at_help import ruser_id
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_102, WAVES_CODE_103
from ..utils.hint import error_reply
from ..utils.waves_api import waves_api
from .draw_role_info import draw_role_img

waves_role_info = SV("waves查询信息")


@waves_role_info.on_fullmatch(("查询", "卡片"), block=True)
async def send_role_info(bot: Bot, ev: Event):
    logger.info("[鸣潮]开始执行[查询信息]")
    user_id = ruser_id(ev)
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    logger.info(f"[鸣潮][查询信息] user_id: {user_id} UID: {uid}")
    if not uid:
        await bot.send(error_reply(WAVES_CODE_103))
        return

    _, ck = await waves_api.get_ck_result(uid, user_id, ev.bot_id)
    if not ck:
        await bot.send(error_reply(WAVES_CODE_102))
        return

    im = await draw_role_img(uid, ck, ev)
    await bot.send(im)  # type: ignore
