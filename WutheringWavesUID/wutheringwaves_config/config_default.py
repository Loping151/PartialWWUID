from typing import Dict

from gsuid_core.utils.plugins_config.models import (
    GSC,
    GsBoolConfig,
    GsDictConfig,
    GsIntConfig,
    GsListConfig,
    GsListStrConfig,
    GsStrConfig,
)

CONFIG_DEFAULT: Dict[str, GSC] = {
    "WavesAnnGroups": GsDictConfig(
        "推送公告群组",
        "鸣潮公告推送群组",
        {},
    ),
    "WavesAnnNewIds": GsListConfig(
        "推送公告ID",
        "鸣潮公告推送ID列表",
        [],
    ),
    "WavesAnnOpen": GsBoolConfig(
        "公告推送总开关",
        "公告推送总开关",
        True,
    ),
    "WavesRankUseTokenGroup": GsListStrConfig(
        "有token才能进排行，群管理可设置",
        "有token才能进排行，群管理可设置",
        [],
    ),
    "WavesRankNoLimitGroup": GsListStrConfig(
        "无限制进排行，群管理可设置",
        "无限制进排行，群管理可设置",
        [],
    ),
    "WavesGuide": GsListStrConfig(
        "角色攻略图提供方",
        "使用ww角色攻略时选择的提供方",
        ["all"],
        options=[
            "all",
            "小羊早睡不遭罪",
            "金铃子攻略组",
            "結星",
            "Moealkyne",
            "小沐XMu",
            "吃我无痕",
        ],
    ),
    "WavesLoginUrl": GsStrConfig(
        "鸣潮登录url",
        "用于设置WutheringWavesUID登录界面的配置",
        "",
    ),
    "WavesLoginUrlSelf": GsBoolConfig(
        "强制【鸣潮登录url】为自己的域名",
        "强制【鸣潮登录url】为自己的域名",
        False,
    ),
    "WavesTencentWord": GsBoolConfig(
        "腾讯文档",
        "腾讯文档",
        False,
    ),
    "WavesQRLogin": GsBoolConfig(
        "开启后，登录链接变成二维码",
        "开启后，登录链接变成二维码",
        False,
    ),
    "WavesLoginForward": GsBoolConfig(
        "开启后，登录链接变为转发消息",
        "开启后，登录链接变为转发消息",
        False,
    ),
    "WavesOnlySelfCk": GsBoolConfig(
        "所有查询使用自己的ck",
        "所有查询使用自己的ck",
        False,
    ),
    "QQPicCache": GsBoolConfig(
        "排行榜qq头像缓存开关",
        "排行榜qq头像缓存开关",
        False,
    ),
    "RankUseToken": GsBoolConfig(
        "有token才能进排行",
        "有token才能进排行",
        False,
    ),
    "DelInvalidCookie": GsBoolConfig(
        "每天定时删除无效token",
        "每天定时删除无效token",
        False,
    ),
    "AnnMinuteCheck": GsIntConfig(
        "公告推送时间检测（单位min）", "公告推送时间检测（单位min）", 10, 60
    ),
    "RefreshInterval": GsIntConfig(
        "刷新面板间隔，重启生效（单位秒）",
        "刷新面板间隔，重启生效（单位秒）",
        0,
        600,
    ),
    "RefreshIntervalNotify": GsStrConfig(
        "刷新面板间隔通知文案",
        "刷新面板间隔通知文案",
        "请等待{}s后尝试刷新面板！",
    ),
    "HideUid": GsBoolConfig(
        "隐藏uid",
        "隐藏uid",
        False,
    ),
    "RoleListQuery": GsBoolConfig(
        "是否可以使用uid直接查询练度",
        "是否可以使用uid直接查询练度",
        True,
    ),
    "MaxBindNum": GsIntConfig(
        "绑定特征码限制数量（未登录）", "绑定特征码限制数量（未登录）", 2, 100
    ),
    "WavesToken": GsStrConfig(
        "鸣潮全排行token",
        "鸣潮全排行token",
        "",
    ),
    "AtCheck": GsBoolConfig(
        "开启可以艾特查询",
        "开启可以艾特查询",
        True,
    ),
    "KuroUrlProxyUrl": GsStrConfig(
        "库洛域名代理（重启生效）",
        "库洛域名代理（重启生效）",
        "",
    ),
    "LocalProxyUrl": GsStrConfig(
        "本地代理地址",
        "本地代理地址",
        "",
    ),
    "NeedProxyFunc": GsListStrConfig(
        "需要代理的函数",
        "需要代理的函数",
        ["get_role_detail_info"],
        options=[
            "all",
            "get_role_detail_info",
        ],
    ),
    "RefreshCardConcurrency": GsIntConfig(
        "刷新角色面板并发数",
        "刷新角色面板并发数",
        10,
        50,
    ),
    "UseGlobalSemaphore": GsBoolConfig(
        "开启后刷新角色面板并发数为全局共享",
        "开启后刷新角色面板并发数为全局共享",
        False,
    ),
    "CaptchaProvider": GsStrConfig(
        "验证码提供方（重启生效）",
        "验证码提供方（重启生效）",
        "",
        options=["ttorc"],
    ),
    "CaptchaAppKey": GsStrConfig(
        "验证码提供方appkey",
        "验证码提供方appkey",
        "",
    ),
}
