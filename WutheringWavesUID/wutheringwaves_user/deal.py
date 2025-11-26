from typing import List, Optional, Union

from gsuid_core.bot import Bot
from gsuid_core.models import Event

from ..utils.api.api import GAME_ID
from ..utils.api.model import KuroWavesUserInfo
from ..utils.api.request_util import PLATFORM_SOURCE
from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_103
from ..utils.waves_api import waves_api


async def add_cookie(ev: Event, ck: str, did: str) -> str:
    platform = PLATFORM_SOURCE
    kuroWavesUserInfos = await waves_api.get_kuro_role_list(ck, did)
    if (
        not kuroWavesUserInfos.success
        or not kuroWavesUserInfos.data
        or not isinstance(kuroWavesUserInfos.data, list)
    ):
        return kuroWavesUserInfos.throw_msg()

    kuroWavesUserInfos = kuroWavesUserInfos.data

    role_list = []
    for kuroWavesUserInfo in kuroWavesUserInfos:
        data = KuroWavesUserInfo.model_validate(kuroWavesUserInfo)
        if data.gameId != GAME_ID:
            continue

        user = await WavesUser.get_user_by_attr(
            ev.user_id, ev.bot_id, "uid", data.roleId
        )

        succ, bat = await waves_api.get_request_token(
            data.roleId,
            ck,
            did,
            data.serverId,
        )
        if not succ or not bat:
            return bat

        if user:
            await WavesUser.update_data_by_data(
                select_data={
                    "user_id": ev.user_id,
                    "bot_id": ev.bot_id,
                    "uid": data.roleId,
                },
                update_data={
                    "cookie": ck,
                    "status": "",
                    "platform": platform,
                },
            )
        else:
            await WavesUser.insert_data(
                ev.user_id,
                ev.bot_id,
                cookie=ck,
                uid=data.roleId,
                platform=platform,
            )

        # 更新bat
        await WavesUser.update_data_by_data(
            select_data={
                "user_id": ev.user_id,
                "bot_id": ev.bot_id,
                "uid": data.roleId,
            },
            update_data={"bat": bat, "did": did},
        )

        res = await WavesBind.insert_waves_uid(
            ev.user_id, ev.bot_id, data.roleId, ev.group_id, lenth_limit=9
        )
        if res == 0 or res == -2:
            await WavesBind.switch_uid_by_game(ev.user_id, ev.bot_id, data.roleId)

        role_list.append(
            {
                "名字": data.roleName,
                "特征码": data.roleId,
            }
        )

    if len(role_list) == 0:
        return "登录失败\n"

    msg = []
    for role in role_list:
        msg.append(f"[鸣潮]【{role['名字']}】特征码【{role['特征码']}】登录成功!")
    return "\n".join(msg)


async def delete_cookie(ev: Event, uid: str) -> str:
    count = await WavesUser.delete_cookie(uid, ev.user_id, ev.bot_id)
    if count == 0:
        return f"[鸣潮] 特征码[{uid}]的token删除失败!\n❌不存在该特征码的token!\n"
    return f"[鸣潮] 特征码[{uid}]的token删除成功!\n"


async def get_cookie(bot: Bot, ev: Event) -> Union[List[str], str]:
    uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
    if uid_list is None:
        return ERROR_CODE[WAVES_CODE_103]

    msg = []
    for uid in uid_list:
        waves_user: Optional[WavesUser] = await WavesUser.select_waves_user(
            uid, ev.user_id, ev.bot_id
        )
        if not waves_user:
            continue

        ck = await waves_api.get_self_waves_ck(uid, ev.user_id, ev.bot_id)
        if not ck:
            continue
        msg.append(f"鸣潮uid: {uid}")
        msg.append(f"token, did: {waves_user.cookie}, {waves_user.did}")
        msg.append("--------------------------------")

    if not msg:
        return "您当前未绑定token或者token已全部失效\n"

    return msg
