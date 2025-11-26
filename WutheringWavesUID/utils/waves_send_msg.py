import asyncio
import random

from gsuid_core.gss import gss
from gsuid_core.logger import logger
from gsuid_core.subscribe import gs_subscribe
from gsuid_core.utils.boardcast.models import BoardCastMsgDict
from gsuid_core.utils.database.models import Subscribe

board_type = {}


async def send_board_cast_msg(msgs: BoardCastMsgDict, board_cast_type: str):
    logger.info(f"[推送] {board_cast_type} 任务启动...")
    private_msg_list = msgs["private_msg_dict"]
    group_msg_list = msgs["group_msg_dict"]

    subs = await gs_subscribe.get_subscribe(board_type[board_cast_type])

    def get_bot_self_id(qid, bot_id, target_type, group_id):
        if not subs:
            return ""
        for sub in subs:
            sub: Subscribe
            if sub.user_type != target_type:
                continue
            if target_type == "direct":
                if sub.user_id == qid and sub.bot_id == bot_id:
                    return sub.bot_self_id

            if target_type == "group":
                if sub.group_id == group_id and sub.bot_id == bot_id:
                    return sub.bot_self_id
        return ""

    # 执行私聊推送
    for qid in private_msg_list:
        try:
            for bot_id in gss.active_bot:
                for single in private_msg_list[qid]:
                    bot_self_id = get_bot_self_id(qid, single["bot_id"], "direct", "")
                    await gss.active_bot[bot_id].target_send(
                        single["messages"],
                        "direct",
                        qid,
                        single["bot_id"],
                        bot_self_id,
                        "",
                    )
        except Exception as e:
            logger.exception(f"[推送] {qid} 私聊推送失败!错误信息", e)
        await asyncio.sleep(0.5 + random.randint(1, 3))
    logger.info(f"[推送] {board_cast_type} 私聊推送完成!")

    # 执行群聊推送
    for gid in group_msg_list:
        try:
            for bot_id in gss.active_bot:
                if isinstance(group_msg_list[gid], list):
                    for group in group_msg_list[gid]:
                        bot_self_id = get_bot_self_id("", group["bot_id"], "group", gid)  # type: ignore
                        await gss.active_bot[bot_id].target_send(
                            group["messages"],  # type: ignore
                            "group",
                            gid,
                            group["bot_id"],  # type: ignore
                            bot_self_id,
                            "",
                        )
                        await asyncio.sleep(0.5 + random.randint(1, 3))
                else:
                    bot_self_id = get_bot_self_id(
                        "", group_msg_list[gid]["bot_id"], "group", gid
                    )
                    await gss.active_bot[bot_id].target_send(
                        group_msg_list[gid]["messages"],
                        "group",
                        gid,
                        group_msg_list[gid]["bot_id"],
                        bot_self_id,
                        "",
                    )
        except Exception as e:
            logger.exception(f"[推送] 群 {gid} 推送失败!错误信息", e)
        await asyncio.sleep(0.5 + random.randint(1, 3))
    logger.info(f"[推送] {board_cast_type} 群聊推送完成!")
    logger.info(f"[推送] {board_cast_type} 任务结束!")
