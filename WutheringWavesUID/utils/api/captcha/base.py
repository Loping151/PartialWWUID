from abc import ABC, abstractmethod
from typing import Any, Dict, Union

from pydantic import BaseModel


class CaptchaResult(BaseModel):
    captcha_id: str
    lot_number: str
    pass_token: str
    gen_time: str
    captcha_output: str


class CaptchaSolver(ABC):
    API_BASE = ""
    CAPTCHA_ID = "3afb60f292fa803fa809114b9a89b3f5"

    @classmethod
    @abstractmethod
    def create(cls) -> "CaptchaSolver":
        raise NotImplementedError

    @classmethod
    def get_name(cls) -> str:
        return cls.__name__

    @abstractmethod
    async def solve(self) -> Union[CaptchaResult, Dict[str, Any]]:
        raise NotImplementedError

    async def close(self) -> None:
        pass


class RemoteCaptchaSolver(CaptchaSolver):
    @abstractmethod
    async def get_balance(self) -> str:
        raise NotImplementedError
