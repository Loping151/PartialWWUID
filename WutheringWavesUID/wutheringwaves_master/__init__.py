from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.subscribe import gs_subscribe
from gsuid_core.sv import SV

sv_master = SV("联系主人", pm=0)
master_name_ann = "联系主人"


@sv_master.on_regex(("^(联系|取消联系)主人$"))
async def rover_sign_result(bot: Bot, ev: Event):
    if ev.bot_id != "onebot":
        logger.debug(f"非onebot禁止联系主人 【{ev.bot_id}】")
        return

    if "取消" in ev.raw_text:
        option = "关闭"
    else:
        option = "开启"

    if option == "关闭":
        await gs_subscribe.delete_subscribe("single", master_name_ann, ev)
    else:
        await gs_subscribe.add_subscribe("single", master_name_ann, ev)

    await bot.send(f"[联系主人] 已{option}订阅!")
