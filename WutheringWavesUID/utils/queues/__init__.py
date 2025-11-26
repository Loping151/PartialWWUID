from typing import Any

import httpx

from gsuid_core.logger import logger

from ..api.wwapi import (
    UPLOAD_ABYSS_RECORD_URL,
    UPLOAD_SLASH_RECORD_URL,
    UPLOAD_URL,
)
from .const import QUEUE_ABYSS_RECORD, QUEUE_SCORE_RANK, QUEUE_SLASH_RECORD
from .queues import event_handler, start_dispatcher


@event_handler(QUEUE_SCORE_RANK)
async def send_score_rank(item: Any):
    if not item:
        return
    if not isinstance(item, dict):
        return
    from ...wutheringwaves_config import WutheringWavesConfig

    WavesToken = WutheringWavesConfig.get_config("WavesToken").data

    if not WavesToken:
        return

    async with httpx.AsyncClient() as client:
        res = None
        try:
            res = await client.post(
                UPLOAD_URL,
                json=item,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {WavesToken}",
                },
                timeout=httpx.Timeout(10),
            )
            logger.info(f"上传面板结果: {res.status_code} - {res.text}")
        except Exception as e:
            logger.exception(f"上传面板失败: {res.text if res else ''} {e}")


@event_handler(QUEUE_ABYSS_RECORD)
async def send_abyss_record(item: Any):
    if not item:
        return
    if not isinstance(item, dict):
        return
    from ...wutheringwaves_config import WutheringWavesConfig

    WavesToken = WutheringWavesConfig.get_config("WavesToken").data

    if not WavesToken:
        return

    async with httpx.AsyncClient() as client:
        res = None
        try:
            res = await client.post(
                UPLOAD_ABYSS_RECORD_URL,
                json=item,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {WavesToken}",
                },
                timeout=httpx.Timeout(10),
            )
            logger.info(f"上传深渊结果: {res.status_code} - {res.text}")
        except Exception as e:
            logger.exception(f"上传深渊失败: {res.text if res else ''} {e}")


@event_handler(QUEUE_SLASH_RECORD)
async def send_slash_record(item: Any):
    if not item:
        return
    if not isinstance(item, dict):
        return
    from ...wutheringwaves_config import WutheringWavesConfig

    WavesToken = WutheringWavesConfig.get_config("WavesToken").data

    if not WavesToken:
        return

    async with httpx.AsyncClient() as client:
        res = None
        try:
            res = await client.post(
                UPLOAD_SLASH_RECORD_URL,
                json=item,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {WavesToken}",
                },
                timeout=httpx.Timeout(10),
            )
            logger.info(f"上传冥海结果: {res.status_code} - {res.text}")
        except Exception as e:
            logger.exception(f"上传冥海失败: {res.text if res else ''} {e}")


def init_queues():
    # 启动任务分发器
    start_dispatcher(daemon=True)
