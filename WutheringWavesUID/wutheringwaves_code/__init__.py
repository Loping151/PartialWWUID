import json
import re
import time
from datetime import datetime

import httpx

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV

sv_waves_code = SV("鸣潮兑换码")

invalid_code_list = ("MINGCHAO",)

url = "https://newsimg.5054399.com/comm/mlcxqcommon/static/wap/js/data_102.js?{}&callback=?&_={}"


@sv_waves_code.on_fullmatch((f"code", f"兑换码"))
async def get_sign_func(bot: Bot, ev: Event):
    code_list = await get_code_list()
    if not code_list:
        return await bot.send("[获取兑换码失败] 请稍后再试")

    msgs = []
    for code in code_list:
        is_fail = code.get("is_fail", "0")
        if is_fail == "1":
            continue
        order = code.get("order", "")
        if order in invalid_code_list or not order:
            continue
        reward = code.get("reward", "")
        label = code.get("label", "")
        msg = [f"兑换码: {order}", f"奖励: {reward}", label]
        msgs.append("\n".join(msg))

    await bot.send(msgs)


async def get_code_list():
    try:
        now = datetime.now()
        time_string = f"{now.year - 1900}{now.month - 1}{now.day}{now.hour}{now.minute}"
        now_time = int(time.time() * 1000)
        new_url = url.format(time_string, now_time)
        async with httpx.AsyncClient(timeout=None) as client:
            res = await client.get(new_url, timeout=10)
            json_data = res.text.split("=", 1)[1].strip().rstrip(";")
            logger.debug(f"[获取兑换码] url:{new_url}, codeList:{json_data}")
            return json.loads(json_data)

    except Exception as e:
        logger.exception("[获取兑换码失败] ", e)
        return


def is_code_expired(label: str) -> bool:
    if not label:
        return False

    # 使用正则提取月份和日期
    pattern = r"(\d{1,2})月(\d{1,2})日(\d{1,2})点"
    match = re.search(pattern, label)
    if not match:
        return False

    expire_month = int(match.group(1))
    expire_day = int(match.group(2))
    expire_hour = int(match.group(2))

    now = datetime.now()
    current_month = now.month

    expire_year = now.year
    # 处理跨年的情况
    if current_month < expire_month:
        # 当前月份小于截止月份，说明截止日期是去年的
        expire_year -= 1
    elif current_month == expire_month:
        # 当前月份等于截止月份，需要比较日期
        if now.day > expire_day:
            # 当前日期已经过了截止日期，说明是明年的
            expire_year += 1
    else:
        # 当前月份大于截止月份，使用当前年份
        pass

    if expire_hour == 24:
        expire_hour = 23
        expire_min = 59
        expire_sec = 59
    else:
        expire_min = 0
        expire_sec = 0

    # 构建截止时间
    expire_date = datetime(
        expire_year, expire_month, expire_day, expire_hour, expire_min, expire_sec
    )

    # 比较时间
    return now > expire_date
