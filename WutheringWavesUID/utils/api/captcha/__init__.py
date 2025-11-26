import importlib
import pkgutil
from typing import Dict, Optional, Type

from gsuid_core.logger import logger

from ...resource.RESOURCE_PATH import CAPTCHA_PATH
from .base import CaptchaSolver

SOLVER_REGISTRY: Dict[str, Type[CaptchaSolver]] = {}


def register_solver(name: str):
    def decorator(cls: Type[CaptchaSolver]):
        SOLVER_REGISTRY[name] = cls
        return cls

    return decorator


def _auto_discover_solvers():
    global SOLVER_REGISTRY
    if SOLVER_REGISTRY:
        return
    package_path = CAPTCHA_PATH
    package_name = __package__

    for module_info in pkgutil.iter_modules([str(package_path)]):
        # 排除非求解器模块 (例如基类、错误定义等)
        if module_info.name not in ("base", "errors"):
            try:
                full_module_name = f"{package_name}.{module_info.name}"
                importlib.import_module(full_module_name)
            except Exception as e:
                logger.warning(f"无法导入求解器模块 {module_info.name}: {e}")


# 在包导入时运行发现机制
_auto_discover_solvers()


def get_solver() -> Optional[CaptchaSolver]:
    from ....wutheringwaves_config import WutheringWavesConfig

    captcha_provider = WutheringWavesConfig.get_config("CaptchaProvider").data
    if not captcha_provider:
        return None

    solver_class = SOLVER_REGISTRY.get(captcha_provider)

    logger.info(f"获取验证码求解器: {SOLVER_REGISTRY}")

    if solver_class:
        return solver_class.create()

    return None
