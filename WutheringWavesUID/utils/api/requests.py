import asyncio
import inspect
import json
import random
from typing import Any, Dict, List, Literal, Mapping, Optional, Union

import aiohttp
from aiohttp import ClientTimeout, ContentTypeError

from gsuid_core.logger import logger

from ...utils.database.models import WavesUser
from ...wutheringwaves_config import WutheringWavesConfig
from ..error_reply import WAVES_CODE_999
from ..util import timed_async_cache
from .api import (
    ANN_CONTENT_URL,
    ANN_LIST_URL,
    BASE_DATA_URL,
    BATCH_ROLE_COST,
    CALABASH_DATA_URL,
    CALCULATOR_REFRESH_DATA_URL,
    CHALLENGE_DATA_URL,
    EXPLORE_DATA_URL,
    GACHA_LOG_URL,
    GACHA_NET_LOG_URL,
    GAME_ID,
    LOGIN_LOG_URL,
    LOGIN_URL,
    MONTH_LIST_URL,
    MORE_ACTIVITY_URL,
    MR_REFRESH_URL,
    NET_SERVER_ID_MAP,
    ONLINE_LIST_PHANTOM,
    ONLINE_LIST_ROLE,
    ONLINE_LIST_WEAPON,
    PERIOD_LIST_URL,
    QUERY_OWNED_ROLE,
    REFRESH_URL,
    REQUEST_TOKEN,
    ROLE_CULTIVATE_STATUS,
    ROLE_DATA_URL,
    ROLE_DETAIL_URL,
    ROLE_LIST_URL,
    SERVER_ID,
    SERVER_ID_NET,
    SLASH_DETAIL_URL,
    SLASH_INDEX_URL,
    TOWER_DETAIL_URL,
    TOWER_INDEX_URL,
    VERSION_LIST_URL,
    WEEK_LIST_URL,
    WIKI_DETAIL_URL,
    WIKI_ENTRY_DETAIL_URL,
    WIKI_HOME_URL,
    WIKI_TREE_URL,
    get_local_proxy_url,
    get_need_proxy_func,
)
from .captcha import get_solver
from .captcha.base import CaptchaResult
from .captcha.errors import CaptchaError
from .request_util import (
    KURO_VERSION,
    KuroApiResp,
    get_base_header,
    get_community_header,
)


class WavesApi:
    ssl_verify = True
    ann_map = {}
    ann_list_data = []
    event_type = {"2": "资讯", "3": "公告", "1": "活动"}

    entry_detail_map = {}

    _sessions: Dict[str, aiohttp.ClientSession] = {}
    _session_lock = asyncio.Lock()

    def __init__(self):
        self.captcha_solver = get_solver()
        if self.captcha_solver:
            logger.success(f"使用过码器: {self.captcha_solver.get_name()}")

    async def get_session(self, proxy: Optional[str] = None) -> aiohttp.ClientSession:
        key = f"{proxy or 'no_proxy'}"

        if key in self._sessions and not self._sessions[key].closed:
            return self._sessions[key]

        async with self._session_lock:
            if key in self._sessions and not self._sessions[key].closed:
                return self._sessions[key]

            session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=self.ssl_verify),
            )

            self._sessions[key] = session
            return session

    def is_net(self, roleId):
        _temp = int(roleId)
        return _temp >= 200000000

    def get_server_id(self, roleId, serverId: Optional[str] = None):
        if serverId:
            return serverId
        if self.is_net(roleId):
            return NET_SERVER_ID_MAP.get(int(roleId) // 100000000, SERVER_ID_NET)
        return SERVER_ID

    async def refresh_bat_token(self, waves_user: WavesUser):
        success, access_token = await self.get_request_token(
            waves_user.uid, waves_user.cookie, waves_user.did
        )
        if not success:
            return waves_user

        waves_user.bat = access_token
        await WavesUser.update_data_by_data(
            select_data={
                # "user_id": waves_user.user_id,
                # "bot_id": waves_user.bot_id,
                "uid": waves_user.uid,
            },
            update_data={"bat": access_token},
        )
        return waves_user

    async def get_used_headers(
        self, cookie: str, uid: str, needToken=False
    ) -> Dict[str, Any]:
        headers = {
            # "token": cookie,
            "did": "",
            "b-at": "",
        }
        if needToken:
            headers["token"] = cookie
        waves_user: Optional[WavesUser] = await WavesUser.select_data_by_cookie_and_uid(
            cookie=cookie,
            uid=uid,
        ) or await WavesUser.select_data_by_cookie(
            cookie=cookie,
        )

        if not waves_user:
            return headers

        headers["did"] = waves_user.did or ""
        headers["b-at"] = waves_user.bat or ""
        return headers

    async def get_ck_result(self, uid, user_id, bot_id) -> tuple[bool, Optional[str]]:
        ck = await self.get_self_waves_ck(uid, user_id, bot_id)
        if ck:
            return True, ck
        ck = await self.get_waves_random_cookie(uid, user_id)
        return False, ck

    async def get_self_waves_ck(
        self, uid: str, user_id: str, bot_id: str
    ) -> Optional[str]:
        # 返回空串 表示绑定已失效
        waves_user = await WavesUser.select_waves_user(uid, user_id, bot_id)
        if not waves_user or not waves_user.cookie:
            return ""

        if waves_user.status == "无效":
            return ""

        data = await self.login_log(uid, waves_user.cookie)
        if not data.success:
            await data.mark_cookie_invalid(uid, waves_user.cookie)
            return ""

        data = await self.refresh_data(uid, waves_user.cookie)
        if not data.success:
            if data.is_bat_token_invalid:
                if waves_user := await self.refresh_bat_token(waves_user):
                    return waves_user.cookie
            else:
                await data.mark_cookie_invalid(uid, waves_user.cookie)
            return ""

        return waves_user.cookie

    async def get_waves_random_cookie(self, uid: str, user_id: str) -> Optional[str]:
        if WutheringWavesConfig.get_config("WavesOnlySelfCk").data:
            return None

        # 公共ck 随机一个
        user_list = await WavesUser.get_waves_all_user()
        random.shuffle(user_list)
        ck_list = []
        times = 1
        for user in user_list:
            if not await WavesUser.cookie_validate(user.uid):
                continue

            data = await self.login_log(user.uid, user.cookie)
            if not data.success:
                await data.mark_cookie_invalid(user.uid, user.cookie)
                continue

            data = await self.refresh_data(user.uid, user.cookie)
            if not data.success:
                await data.mark_cookie_invalid(user.uid, user.cookie)

                if times <= 0:
                    break

                times -= 1
                continue

            ck_list.append(user.cookie)
            break

        if len(ck_list) > 0:
            return random.choices(ck_list, k=1)[0]

    async def get_kuro_role_list(self, token: str, did: str):
        header = await get_base_header()
        header.update(
            {
                "token": token,
                "devCode": did,
            }
        )
        data = {"gameId": GAME_ID}

        return await self._waves_request(ROLE_LIST_URL, "POST", header, data=data)

    async def get_daily_info(
        self, roleId: str, token: str, gameId: Union[str, int] = GAME_ID
    ):
        """每日"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(
            cookie=token, uid=roleId, needToken=True
        )
        header.update(used_headers)
        data = {
            "type": "1",
            "sizeType": "2",
            "gameId": gameId,
            "serverId": self.get_server_id(roleId),
            "roleId": roleId,
        }
        return await self._waves_request(
            MR_REFRESH_URL,
            "POST",
            header,
            data=data,
        )

    async def refresh_data(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ):
        """刷新数据"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(REFRESH_URL, "POST", header, data=data)

    async def login_log(self, roleId: str, token: str):
        """登录校验"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(
            {
                "token": token,
                "devCode": used_headers.get("did", ""),
                "version": KURO_VERSION,
            }
        )

        data = {}
        return await self._waves_request(LOGIN_LOG_URL, "POST", header, data=data)

    async def get_base_info(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ):
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)

        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(BASE_DATA_URL, "POST", header, data=data)

    async def get_role_info(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ):
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)

        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(ROLE_DATA_URL, "POST", header, data=data)

    async def get_tree(self):
        header = await get_community_header()
        header.update({"wiki_type": "9"})
        data = {"devcode": ""}
        return await self._waves_request(WIKI_TREE_URL, "POST", header, data=data)

    async def get_wiki(self, catalogueId: str):
        header = await get_community_header()
        header.update({"wiki_type": "9"})
        data = {"catalogueId": catalogueId, "limit": 1000}
        return await self._waves_request(WIKI_DETAIL_URL, "POST", header, data=data)

    async def get_role_detail_info(
        self, charId: str, roleId: str, token: str, serverId: Optional[str] = None
    ):
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)

        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
            "channelId": "19",
            "countryCode": "1",
            "id": charId,
        }
        return await self._waves_request(ROLE_DETAIL_URL, "POST", header, data=data)

    async def get_calabash_data(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ):
        """数据坞"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)

        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(CALABASH_DATA_URL, "POST", header, data=data)

    async def get_explore_data(
        self,
        roleId: str,
        token: str,
        serverId: Optional[str] = None,
        countryCode: str = "1",
    ):
        """探索度"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)

        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
            "countryCode": countryCode,
        }
        return await self._waves_request(EXPLORE_DATA_URL, "POST", header, data=data)

    async def get_challenge_data(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ):
        """全息"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)

        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(CHALLENGE_DATA_URL, "POST", header, data=data)

    async def get_abyss_data(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ):
        """深渊"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)
        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(TOWER_DETAIL_URL, "POST", header, data=data)

    async def get_abyss_index(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ):
        """深渊"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)

        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(TOWER_INDEX_URL, "POST", header, data=data)

    async def get_slash_index(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ):
        """冥海"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)

        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(SLASH_INDEX_URL, "POST", header, data=data)

    async def get_slash_detail(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ):
        """冥海"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)

        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(SLASH_DETAIL_URL, "POST", header, data=data)

    async def get_more_activity(
        self, roleId: str, token: str, serverId: Optional[str] = None
    ):
        """浸梦海床+激斗！向着荣耀之丘"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(cookie=token, uid=roleId)
        header.update(used_headers)

        data = {
            "gameId": GAME_ID,
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(MORE_ACTIVITY_URL, "POST", header, data=data)

    async def get_request_token(
        self, roleId: str, token: str, did: str, serverId: Optional[str] = None
    ) -> tuple[bool, str]:
        """请求token"""
        header = await get_base_header()
        header.update(
            {
                "token": token,
                "did": did,
                "b-at": "",
            }
        )
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        raw_data = await self._waves_request(REQUEST_TOKEN, "POST", header, data=data)
        if raw_data.success and isinstance(raw_data.data, dict):
            if accessToken := raw_data.data.get("accessToken", ""):
                return True, accessToken

        return False, ""

    async def calculator_refresh_data(
        self,
        roleId: str,
        token: str,
        serverId: Optional[str] = None,
    ):
        header = await get_base_header()
        used_headers = await self.get_used_headers(
            cookie=token, uid=roleId, needToken=True
        )
        header.update(used_headers)

        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(
            CALCULATOR_REFRESH_DATA_URL, "POST", header, data=data
        )

    @timed_async_cache(
        86400,
        lambda x: x.success and isinstance(x.data, (dict, list)),
    )
    async def get_online_list_role(self, token: str):
        """所有的角色列表"""
        header = await get_base_header()
        header.update({"token": token})
        data = {}
        return await self._waves_request(ONLINE_LIST_ROLE, "POST", header, data=data)

    @timed_async_cache(
        86400,
        lambda x: x.success and isinstance(x.data, (dict, list)),
    )
    async def get_online_list_weapon(self, token: str):
        """所有的武器列表"""
        header = await get_base_header()
        header.update({"token": token})
        data = {}
        return await self._waves_request(ONLINE_LIST_WEAPON, "POST", header, data=data)

    @timed_async_cache(
        86400,
        lambda x: x.success and isinstance(x.data, (dict, list)),
    )
    async def get_online_list_phantom(self, token: str):
        """所有的声骸列表"""
        header = await get_base_header()
        header.update({"token": token})
        data = {}
        return await self._waves_request(ONLINE_LIST_PHANTOM, "POST", header, data=data)

    async def get_owned_role(
        self,
        roleId: str,
        token: str,
        serverId: Optional[str] = None,
    ):
        """已拥有角色"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(
            cookie=token, uid=roleId, needToken=True
        )
        header.update(used_headers)
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
        }
        return await self._waves_request(QUERY_OWNED_ROLE, "POST", header, data=data)

    async def get_develop_role_cultivate_status(
        self,
        roleId: str,
        token: str,
        char_ids: List[str],
        serverId: Optional[str] = None,
    ):
        """角色培养状态"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(
            cookie=token, uid=roleId, needToken=True
        )
        header.update(used_headers)
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
            "ids": ",".join(char_ids),
        }
        return await self._waves_request(
            ROLE_CULTIVATE_STATUS, "POST", header, data=data
        )

    async def get_batch_role_cost(
        self,
        roleId: str,
        token: str,
        content: List[Any],
        serverId: Optional[str] = None,
    ):
        """角色培养成本"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(
            cookie=token, uid=roleId, needToken=True
        )
        header.update(used_headers)
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
            "content": json.dumps(content),
        }
        return await self._waves_request(BATCH_ROLE_COST, "POST", header, data=data)

    async def get_period_list(
        self,
        roleId: str,
        token: str,
    ):
        """资源简报列表"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(
            cookie=token, uid=roleId, needToken=True
        )
        header.update(used_headers)
        return await self._waves_request(PERIOD_LIST_URL, "GET", header)

    async def get_period_detail(
        self,
        type: Literal["month", "week", "version"],
        period: Union[str, int],
        roleId: str,
        token: str,
        serverId: Optional[str] = None,
    ):
        """资源简报详情"""
        header = await get_base_header()
        used_headers = await self.get_used_headers(
            cookie=token, uid=roleId, needToken=True
        )
        header.update(used_headers)
        data = {
            "serverId": self.get_server_id(roleId, serverId),
            "roleId": roleId,
            "period": period,
        }
        if type == "month":
            url = MONTH_LIST_URL
        elif type == "week":
            url = WEEK_LIST_URL
        elif type == "version":
            url = VERSION_LIST_URL
        return await self._waves_request(url, "POST", header, data=data)

    async def get_gacha_log(
        self,
        cardPoolType: str,
        recordId: str,
        roleId: str,
        serverId: Optional[str] = None,
    ):
        """抽卡记录"""
        header = {"Content-Type": "application/json;charset=UTF-8"}
        data = {
            "playerId": roleId,
            "cardPoolType": cardPoolType,
            "serverId": self.get_server_id(roleId, serverId),
            "languageCode": "zh-Hans",
            "recordId": recordId,
        }
        url = GACHA_NET_LOG_URL if self.is_net(roleId) else GACHA_LOG_URL
        return await self._waves_request(url, "POST", header, json_data=data)

    async def get_ann_list_by_type(
        self, eventType: str = "", pageSize: Optional[int] = None
    ):
        """获取公告列表"""
        data: Dict[str, Any] = {"gameId": GAME_ID}
        if eventType:
            data.update({"eventType": eventType})
        if pageSize:
            data.update({"pageSize": pageSize})
        headers = await get_community_header()
        return await self._waves_request(ANN_LIST_URL, "POST", headers, data=data)

    async def get_ann_detail(self, post_id: str):
        """获取公告详情"""
        if post_id in self.ann_map:
            return self.ann_map[post_id]

        headers = await get_community_header()
        headers.update({"token": "", "devcode": ""})
        data = {"isOnlyPublisher": 1, "postId": post_id, "showOrderType": 2}
        res = await self._waves_request(ANN_CONTENT_URL, "POST", headers, data=data)
        if res.success:
            raw_data = res.model_dump()
            self.ann_map[post_id] = raw_data["data"]["postDetail"]
            return raw_data["data"]["postDetail"]
        return {}

    async def get_ann_list(self, is_cache: bool = False):
        """获取公告列表"""
        if is_cache and self.ann_list_data:
            return self.ann_list_data

        self.ann_list_data = []
        for _event in self.event_type.keys():
            res = await self.get_ann_list_by_type(eventType=_event, pageSize=5)
            if res.success:
                raw_data = res.model_dump()
                value = [{**x, "id": int(x["id"])} for x in raw_data["data"]["list"]]
                self.ann_list_data.extend(value)

        return self.ann_list_data

    async def get_wiki_home(self):
        """获取wiki首页"""
        headers = await get_community_header()
        headers.update({"wiki_type": "9"})
        res = await self._waves_request(WIKI_HOME_URL, "POST", headers)
        if res.success:
            return res.model_dump()
        return {}

    async def get_entry_detail(self, entry_id: str):
        """获取entry详情"""
        if entry_id in self.entry_detail_map:
            return self.entry_detail_map[entry_id]

        headers = await get_community_header()
        headers.update({"wiki_type": "9"})
        data = {"id": entry_id}
        res = await self._waves_request(
            WIKI_ENTRY_DETAIL_URL, "POST", headers, data=data
        )
        if res.success:
            raw_data = res.model_dump()
            self.entry_detail_map[entry_id] = raw_data
            return raw_data
        return {}

    async def login(self, mobile: Union[int, str], code: str, did: str):
        """登录
        Args:
            mobile (Union[int, str]): 手机号
            code (str): 验证码
            did (str): 设备ID
        """
        header = await get_base_header()
        data = {
            "mobile": mobile,
            "code": code,
            "devCode": did,
        }
        return await self._waves_request(LOGIN_URL, "POST", header, data=data)

    async def _waves_request(
        self,
        url: str,
        method: Literal["GET", "POST"] = "GET",
        header: Optional[Mapping[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> KuroApiResp[Union[str, Dict[str, Any], List[Any]]]:
        if header is None:
            header = await get_base_header()

        proxy_func = get_need_proxy_func()
        if inspect.stack()[1].function in proxy_func or "all" in proxy_func:
            proxy_url = get_local_proxy_url()
        else:
            proxy_url = None

        async def do_request(
            req_data, client_session: aiohttp.ClientSession
        ) -> KuroApiResp[Any]:
            async with client_session.request(
                method,
                url=url,
                headers=header,
                params=params,
                json=json_data,
                data=req_data,
                proxy=proxy_url,
                timeout=ClientTimeout(total=10),
            ) as resp:
                try:
                    raw_data = await resp.json()
                except ContentTypeError:
                    _raw_data = await resp.text()
                    raw_data = {"code": WAVES_CODE_999, "data": _raw_data}

                if isinstance(raw_data, dict):
                    try:
                        raw_data["data"] = json.loads(raw_data.get("data", ""))
                    except Exception:
                        pass

                logger.debug(
                    f"url:[{url}] params:[{params}] headers:[{header}] data:[{req_data}] raw_data:{raw_data}"
                )
                # 统一解析为 KuroApiResp
                return KuroApiResp[Any].model_validate(raw_data)

        async def solve_captcha():
            if not self.captcha_solver:
                return
            for _ in range(max_retries):
                try:
                    return await self.captcha_solver.solve()
                except CaptchaError as e:
                    logger.error(f"url:[{url}] 验证码破解失败: {e}")

            return {"code": WAVES_CODE_999, "data": "验证码破解失败"}

        for attempt in range(max_retries):
            try:
                client = await self.get_session(proxy=proxy_url)
                if not client:
                    logger.warning(f"url:[{url}] 获取session失败")
                    continue

                response = await do_request(data, client)

                res_data = response.data or {}
                if (
                    self.captcha_solver
                    and isinstance(res_data, dict)
                    and res_data.get("geeTest") is True
                ):
                    seccode_data = await solve_captcha()
                    if isinstance(seccode_data, CaptchaResult):
                        seccode_data = seccode_data.model_dump_json()

                    if isinstance(seccode_data, dict):
                        seccode_data = json.dumps(seccode_data)

                    # 重试数据准备
                    retry_data = data.copy() if data else {}
                    retry_data["geeTestData"] = seccode_data
                    return await do_request(retry_data, client)

                return response

            except aiohttp.ClientError as e:
                logger.warning(f"url:[{url}] 网络请求失败, 尝试次数 {attempt + 1}", e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
            except Exception as e:
                logger.warning(f"url:[{url}] 发生未知错误, 尝试次数 {attempt + 1}", e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)

        return KuroApiResp[Any].err(
            "请求服务器失败，已达最大重试次数", code=WAVES_CODE_999
        )
