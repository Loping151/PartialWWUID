import asyncio
import random

from gsuid_core.aps import scheduler
from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.subscribe import gs_subscribe
from gsuid_core.sv import SV

from ..utils.waves_api import waves_api
from ..wutheringwaves_config import WutheringWavesConfig
from .ann_card import ann_detail_card, ann_list_card

sv_ann = SV("鸣潮公告")
sv_ann_sub = SV("订阅鸣潮公告", pm=3)

task_name_ann = "订阅鸣潮公告"
ann_minute_check: int = WutheringWavesConfig.get_config("AnnMinuteCheck").data


@sv_ann.on_command("公告")
async def ann_(bot: Bot, ev: Event):
    ann_id = ev.text
    if not ann_id:
        img = await ann_list_card()
        return await bot.send(img)

    ann_id = ann_id.replace("#", "")
    if not ann_id.isdigit():
        raise Exception("公告ID不正确")

    img = await ann_detail_card(int(ann_id))
    return await bot.send(img)  # type: ignore


@sv_ann_sub.on_fullmatch("订阅公告")
async def sub_ann_(bot: Bot, ev: Event):
    if ev.bot_id != "onebot":
        logger.debug(f"非onebot禁止订阅鸣潮公告 【{ev.bot_id}】")
        return

    if ev.group_id is None:
        return await bot.send("请在群聊中订阅")
    if not WutheringWavesConfig.get_config("WavesAnnOpen").data:
        return await bot.send("鸣潮公告推送功能已关闭")

    data = await gs_subscribe.get_subscribe(task_name_ann)
    if data:
        for subscribe in data:
            if subscribe.group_id == ev.group_id:
                return await bot.send("已经订阅了鸣潮公告！")

    await gs_subscribe.add_subscribe(
        "session",
        task_name=task_name_ann,
        event=ev,
        extra_message="",
    )

    logger.info(data)
    await bot.send("成功订阅鸣潮公告!")


@sv_ann_sub.on_fullmatch(("取消订阅公告", "取消公告", "退订公告"))
async def unsub_ann_(bot: Bot, ev: Event):
    if ev.bot_id != "onebot":
        logger.debug(f"非onebot禁止订阅鸣潮公告 【{ev.bot_id}】")
        return

    if ev.group_id is None:
        return await bot.send("请在群聊中取消订阅")

    data = await gs_subscribe.get_subscribe(task_name_ann)
    if data:
        for subscribe in data:
            if subscribe.group_id == ev.group_id:
                await gs_subscribe.delete_subscribe("session", task_name_ann, ev)
                return await bot.send("成功取消订阅鸣潮公告!")
    else:
        if not WutheringWavesConfig.get_config("WavesAnnOpen").data:
            return await bot.send("鸣潮公告推送功能已关闭")

    return await bot.send("未曾订阅鸣潮公告！")


@scheduler.scheduled_job("interval", minutes=ann_minute_check)
async def check_waves_ann():
    if not WutheringWavesConfig.get_config("WavesAnnOpen").data:
        return
    await check_waves_ann_state()


async def check_waves_ann_state():
    logger.info("[鸣潮公告] 定时任务: 鸣潮公告查询..")
    datas = await gs_subscribe.get_subscribe(task_name_ann)
    if not datas:
        logger.info("[鸣潮公告] 暂无群订阅")
        return

    ids = WutheringWavesConfig.get_config("WavesAnnNewIds").data
    new_ann_list = await waves_api.get_ann_list()
    if not new_ann_list:
        return

    new_ann_ids = [x["id"] for x in new_ann_list]
    if not ids:
        WutheringWavesConfig.set_config("WavesAnnNewIds", new_ann_ids)
        logger.info("[鸣潮公告] 初始成功, 将在下个轮询中更新.")
        return

    new_ann_need_send = []
    for ann_id in new_ann_ids:
        if ann_id not in ids:
            new_ann_need_send.append(ann_id)

    if not new_ann_need_send:
        logger.info("[鸣潮公告] 没有最新公告")
        return

    logger.info(f"[鸣潮公告] 更新公告id: {new_ann_need_send}")
    save_ids = sorted(ids, reverse=True)[:50] + new_ann_ids
    WutheringWavesConfig.set_config("WavesAnnNewIds", list(set(save_ids)))

    for ann_id in new_ann_need_send:
        try:
            img = await ann_detail_card(ann_id, is_check_time=True)
            if isinstance(img, str):
                continue
            for subscribe in datas:
                await subscribe.send(img)  # type: ignore
                await asyncio.sleep(random.uniform(1, 3))
        except Exception as e:
            logger.exception(e)

    logger.info("[鸣潮公告] 推送完毕")
