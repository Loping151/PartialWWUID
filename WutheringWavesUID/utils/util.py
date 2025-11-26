import asyncio
import inspect
import random
import string
import time
from functools import wraps
from typing import Any, Callable, Coroutine, Dict, List, TypeVar, overload

import httpx

from gsuid_core.subscribe import gs_subscribe


def timed_async_cache(expiration, condition=lambda x: True):
    def decorator(func):
        cache = {}
        locks = {}

        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        is_cls_method = params and params[0] in ["self", "cls"]

        @wraps(func)
        async def wrapper(*args):
            current_time = time.time()
            if is_cls_method and args and hasattr(args[0], "__class__"):
                cache_key = f"{args[0].__class__.__name__}.{func.__name__}"
            else:
                cache_key = func.__name__

            # 为每个缓存键创建一个锁
            if cache_key not in locks:
                locks[cache_key] = asyncio.Lock()

            # 检查缓存，如果有效则直接返回
            if cache_key in cache:
                value, timestamp = cache[cache_key]
                if current_time - timestamp < expiration:
                    return value

            # 获取锁以确保并发安全
            async with locks[cache_key]:
                # 双重检查，避免等待锁期间其他协程已经更新了缓存
                if cache_key in cache:
                    value, timestamp = cache[cache_key]
                    if current_time - timestamp < expiration:
                        return value

                # 执行原始函数
                value = await func(*args)
                if condition(value):
                    cache[cache_key] = (value, current_time)
                return value

        return wrapper

    return decorator


F = TypeVar("F", bound=Callable[..., Coroutine[Any, Any, Any]])


@overload
def async_func_lock(*, keys: List[str] | None = None) -> Callable[[F], F]: ...


@overload
def async_func_lock(_func: F, *, keys: List[str] | None = None) -> F: ...


# 异步函数参数锁
def async_func_lock(
    _func: F | None = None,
    *,
    keys: List[str] | None = None,
) -> Callable[[F], F] | F:
    """
    异步函数参数锁
    使用示例:
    @async_func_lock(keys=["user_id"])
    async def get_user_info(user_id: str, uid: str):
        return await get_user_info(user_id, uid)
    """

    def decorator(func: F) -> F:
        locks: Dict[tuple, asyncio.Lock] = {}
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        is_cls_method = params and params[0] in ["self", "cls"]

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if is_cls_method and args and hasattr(args[0], "__class__"):
                # 对于类方法, 使用实例id来确保锁是实例级别的
                cache_key_parts = [args[0].__class__.__name__, func.__name__]
            else:
                # 对于普通函数, 锁是函数级别的
                cache_key_parts = [func.__name__]

            if keys:
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                for key in keys:
                    if key in bound_args.arguments:
                        cache_key_parts.append(repr(bound_args.arguments[key]))

            lock_key = tuple(cache_key_parts)
            if lock_key not in locks:
                locks[lock_key] = asyncio.Lock()

            async with locks[lock_key]:
                return await func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    if _func is None:
        return decorator
    else:
        return decorator(_func)


# 使用示例
@timed_async_cache(86400)
async def get_public_ip(host="127.127.127.127"):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://event.kurobbs.com/event/ip", timeout=4)
            ip = r.text
            return ip
    except:  # noqa:E722, B001
        pass

    # 尝试从 ipify 获取 IP 地址
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.ipify.org/?format=json", timeout=4)
            ip = r.json()["ip"]
            return ip
    except:  # noqa:E722, B001
        pass

    # 尝试从 httpbin.org 获取 IP 地址
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://httpbin.org/ip", timeout=4)
            ip = r.json()["origin"]
            return ip
    except:  # noqa:E722, B001
        pass

    return host


def generate_random_string(length=32):
    # 定义可能的字符集合
    characters = string.ascii_letters + string.digits + string.punctuation
    # 使用random.choice随机选择字符，并连接成字符串
    random_string = "".join(random.choice(characters) for i in range(length))
    return random_string


def generate_random_ipv6_manual():
    return ":".join([hex(random.randint(0, 0xFFFF))[2:].zfill(4) for _ in range(8)])


def generate_random_ipv4_manual():
    return ".".join([str(random.randint(0, 255)) for _ in range(4)])


def hide_uid(uid: str) -> str:
    from ..wutheringwaves_config import WutheringWavesConfig

    HideUid = WutheringWavesConfig.get_config("HideUid").data
    if not HideUid:
        return uid
    if len(uid) < 2:
        return uid
    return uid[:2] + "*" * 4 + uid[-2:]


def format_with_defaults(desc: str, params: List[Any], default_value: str = "N/A"):
    num_placeholders = desc.count("{")  # 简单估计位置参数数量
    params_list = list(params)
    while len(params_list) < num_placeholders:
        params_list.append(default_value)
    return desc.format(*params_list)


def get_version(dynamic: bool = False, **kwargs):
    from ..version import WutheringWavesUID_version
    if dynamic:
        from ..utils.safety import generate_dynamic_version
        dynamic_version = generate_dynamic_version(**kwargs)
        return WutheringWavesUID_version + dynamic_version

    return WutheringWavesUID_version


filter_msg = [
    "角色查询失败，请重新选择角色",
]


# 发送主人信息
@timed_async_cache(300, lambda x: x)
async def send_master_info(msg: str):
    # 过滤
    for i in filter_msg:
        if i in msg:
            return

    subscribes = await gs_subscribe.get_subscribe("联系主人")
    if not subscribes:
        return
    if subscribes:
        for sub in subscribes:
            await sub.send(f"【联系主人】：{msg}")
        return True


def login_platform() -> str:
    # from ..wutheringwaves_config import WutheringWavesConfig

    # LoginType = WutheringWavesConfig.get_config("WavesLoginTypeNew").data
    # return LoginType if LoginType else "ios"
    return "ios"
