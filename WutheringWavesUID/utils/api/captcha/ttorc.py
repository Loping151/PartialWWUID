import json
from typing import Any, Dict

import aiohttp

from ..captcha.errors import CaptchaVerifyError
from . import register_solver
from .base import RemoteCaptchaSolver

# ttorc 只是作为参考
# https://www.kancloud.cn/ttorc/ttorc/3119237
ITEM_ID = 42  # 四代滑块


@register_solver("ttorc")
class TtorcCaptchaSolver(RemoteCaptchaSolver):
    API_BASE = "http://api.ttocr.com"
    API_SOLVE = f"{API_BASE}/api/recognize"

    @classmethod
    def create(cls) -> "TtorcCaptchaSolver":
        from ....wutheringwaves_config import WutheringWavesConfig

        captcha_appkey = WutheringWavesConfig.get_config("CaptchaAppKey").data
        return cls(appkey=captcha_appkey)

    def __init__(
        self,
        appkey: str,
        session: aiohttp.ClientSession | None = None,
    ):
        self._appkey = appkey
        self._session = session or aiohttp.ClientSession()

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def get_balance(self) -> str:
        return "N/A"

    async def solve(self) -> Dict[str, Any]:

        # https://www.kancloud.cn/ttorc/ttorc/3119239
        params = {
            "appkey": self._appkey,
            "gt": self.CAPTCHA_ID,
            "itemid": ITEM_ID,
        }

        try:
            async with self._session.post(
                self.API_SOLVE,
                data=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                resp.raise_for_status()
                ttorc_data = await resp.json()

            if ttorc_data.get("status") != 1:
                raise CaptchaVerifyError(f"Ttorc failed: {ttorc_data.get('msg')}")

            return ttorc_data["resultid"]
        except (aiohttp.ClientError, json.JSONDecodeError) as e:
            raise CaptchaVerifyError(f"Ttorc request failed: {e}") from e
        except Exception as e:
            raise CaptchaVerifyError(f"Invalid response from ttorc: {e}") from e
