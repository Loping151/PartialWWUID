from gsuid_core.logger import logger
from gsuid_core.models import Event

from ..utils.database.models import WavesUser

WAVES_USER_MAP = {"体力背景": "stamina_bg"}


async def set_waves_user_value(ev: Event, func: str, uid: str, value: str):
    if func in WAVES_USER_MAP:
        status = WAVES_USER_MAP[func]
    else:
        return "该配置项不存在!\n"
    logger.info("[设置{}] uid:{} value: {}".format(func, uid, value))
    if (
        await WavesUser.update_data_by_data(
            select_data={"user_id": ev.user_id, "bot_id": ev.bot_id, "uid": uid},
            update_data={f"{status}_value": value},
        )
        == 0
    ):
        return f"设置成功!\n特征码[{uid}]\n当前{func}:{value}\n"
    else:
        return "设置失败!\n请检查参数是否正确!\n"
