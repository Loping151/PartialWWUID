import re

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..wutheringwaves_develop.develop import calc_develop_cost

role_develop = SV("waves角色培养")


@role_develop.on_regex(
    r"(?P<develop_list>([\u4e00-\u9fa5]+)(\s+[\u4e00-\u9fa5]+)*?)\s*(养成|培养|培养成本)",
    block=True,
)
async def calc_develop(bot: Bot, ev: Event):
    match = re.search(
        r"(?P<develop_list>([\u4e00-\u9fa5]+)(\s+[\u4e00-\u9fa5]+)*?)\s*(养成|培养|培养成本)",
        ev.raw_text,
    )
    if not match:
        return

    develop_list_str = match.group("develop_list")
    develop_list = develop_list_str.split()
    logger.info(f"养成列表: {develop_list}")

    develop_cost = await calc_develop_cost(ev, develop_list)
    if isinstance(develop_cost, str) or isinstance(develop_cost, bytes):
        return await bot.send(develop_cost)
