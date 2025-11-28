import re

from PIL import Image

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import SV
from gsuid_core.utils.image.convert import convert_img

from ..utils.at_help import is_valid_at, ruser_id
from ..utils.database.models import WavesBind
from ..utils.error_reply import WAVES_CODE_103
from ..utils.hint import error_reply
from ..utils.name_convert import char_name_to_char_id
from ..utils.resource.constant import SPECIAL_CHAR
from ..utils.char_info_utils import PATTERN
from .draw_char_card import draw_char_detail_img, draw_char_score_img
from .upload_card import (
    compress_all_custom_card,
    delete_all_custom_card,
    delete_custom_card,
    get_custom_card_list,
    upload_custom_card,
)

waves_new_get_char_info = SV("waves新获取面板", priority=3)
waves_new_get_one_char_info = SV("waves新获取单个角色面板", priority=3)
waves_new_char_detail = SV("waves新角色面板", priority=4)
waves_char_detail = SV("waves角色面板", priority=5)
waves_upload_char = SV("waves上传面板图", priority=3, pm=1)
waves_char_card_list = SV("waves面板图列表", priority=3, pm=1)
waves_delete_char_card = SV("waves删除面板图", priority=3, pm=1)
waves_delete_all_card = SV("waves删除全部面板图", priority=5, pm=1)
waves_compress_card = SV("waves面板图压缩", priority=5, pm=1)

@waves_new_get_char_info.on_fullmatch(
    (
        "刷新面板",
        "刷新面包",
        "刷新🍞",
        "更新面板",
        "更新🍞",
        "更新面包",
        "强制刷新",
        "面板刷新",
        "面包刷新",
        "🍞刷新",
        "面板更新",
        "面板",
        "面包",
        "🍞",
        "mb",
    ),
    block=True,
)
async def send_card_info(bot: Bot, ev: Event):
    user_id = ruser_id(ev)

    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))

    from .draw_refresh_char_card import draw_refresh_char_detail_img

    buttons = []
    msg = await draw_refresh_char_detail_img(bot, ev, user_id, uid, buttons)
    if isinstance(msg, str) or isinstance(msg, bytes):
        return await bot.send_option(msg, buttons)


@waves_new_get_one_char_info.on_regex(
    rf"^(?P<is_refresh>刷新|更新)(?P<char>{PATTERN})(?P<query_type>面板|面包|🍞|mb)$",
    block=True,
)
async def send_one_char_detail_msg(bot: Bot, ev: Event):
    logger.debug(f"[鸣潮] [角色面板] RAW_TEXT: {ev.raw_text}")
    char = ev.regex_dict.get("char")
    if not char:
        return
    char_id = char_name_to_char_id(char)
    if not char_id or len(char_id) != 4:
        return await bot.send(
            f"[鸣潮] 角色名【{char}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
        )
    refresh_type = [char_id]
    if char_id in SPECIAL_CHAR:
        refresh_type = SPECIAL_CHAR.copy()[char_id]

    user_id = ruser_id(ev)

    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))

    from .draw_refresh_char_card import draw_refresh_char_detail_img

    buttons = []
    msg = await draw_refresh_char_detail_img(
        bot, ev, user_id, uid, buttons, refresh_type
    )
    if isinstance(msg, str) or isinstance(msg, bytes):
        return await bot.send_option(msg, buttons)


@waves_char_detail.on_prefix(("角色面板", "查询"))
async def send_char_detail_msg(bot: Bot, ev: Event):
    char = ev.text.strip(" ")
    logger.debug(f"[鸣潮] [角色面板] CHAR: {char}")
    user_id = ruser_id(ev)
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))
    logger.debug(f"[鸣潮] [角色面板] UID: {uid}")
    if not char:
        return

    im = await draw_char_detail_img(ev, uid, char, user_id)
    if isinstance(im, str) or isinstance(im, bytes):
        return await bot.send(im)


@waves_new_char_detail.on_regex(
    rf"(?P<waves_id>\d+)?(?P<char>{PATTERN})(?P<query_type>面板|面包|🍞|伤害(?P<damage>(\d+)?))(?P<is_pk>pk|对比|PK|比|比较)?(\s*)?(?P<change_list>((换[^换]*)*)?)",
    block=True,
)
async def send_char_detail_msg2(bot: Bot, ev: Event):
    waves_id = ev.regex_dict.get("waves_id")
    char = ev.regex_dict.get("char")
    damage = ev.regex_dict.get("damage")
    query_type = ev.regex_dict.get("query_type")
    is_pk = ev.regex_dict.get("is_pk") is not None
    change_list_regex = ev.regex_dict.get("change_list")

    if waves_id and len(waves_id) != 9:
        return

    if isinstance(query_type, str) and "伤害" in query_type and not damage:
        damage = "1"

    is_limit_query = False
    if isinstance(char, str) and "极限" in char:
        is_limit_query = True
        char = char.replace("极限", "")

    if damage:
        char = f"{char}{damage}"
    if not char:
        return
    logger.debug(f"[鸣潮] [角色面板] CHAR: {char} {ev.regex_dict}")

    if is_limit_query:
        im = await draw_char_detail_img(
            ev, "1", char, ev.user_id, is_limit_query=is_limit_query
        )
        if isinstance(im, str) or isinstance(im, bytes):
            return await bot.send(im)
        else:
            return

    at_sender = True if ev.group_id else False
    if is_pk:
        if not waves_id and not is_valid_at(ev):
            return await bot.send(
                f"[鸣潮] [角色面板] 角色【{char}】PK需要指定目标玩家!\n", at_sender
            )

        uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
        if not uid:
            return await bot.send(error_reply(WAVES_CODE_103))

        im1 = await draw_char_detail_img(
            ev,
            uid,
            char,
            ev.user_id,
            waves_id=None,
            need_convert_img=False,
            is_force_avatar=True,
            change_list_regex=change_list_regex,
        )
        if isinstance(im1, str):
            return await bot.send(im1, at_sender)

        if not isinstance(im1, Image.Image):
            return

        user_id = ruser_id(ev)
        uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
        if not uid:
            return await bot.send(error_reply(WAVES_CODE_103))
        im2 = await draw_char_detail_img(
            ev, uid, char, user_id, waves_id, need_convert_img=False
        )
        if isinstance(im2, str):
            return await bot.send(im2, at_sender)

        if not isinstance(im2, Image.Image):
            return

        # 创建一个新的图片对象
        new_im = Image.new(
            "RGBA", (im1.size[0] + im2.size[0], max(im1.size[1], im2.size[1]))
        )

        # 将两张图片粘贴到新图片对象上
        new_im.paste(im1, (0, 0))
        new_im.paste(im2, (im1.size[0], 0))
        new_im = await convert_img(new_im)
        return await bot.send(new_im)
    else:
        user_id = ruser_id(ev)
        uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
        if not uid:
            return await bot.send(error_reply(WAVES_CODE_103))
        im = await draw_char_detail_img(
            ev, uid, char, user_id, waves_id, change_list_regex=change_list_regex
        )
        at_sender = False
        if isinstance(im, str) or isinstance(im, bytes):
            return await bot.send(im, at_sender)

@waves_new_char_detail.on_regex(rf"^(?P<waves_id>\d+)?(?P<char>{PATTERN})权重$", block=True)
async def send_char_detail_msg2_weight(bot: Bot, ev: Event):
    waves_id = ev.regex_dict.get("waves_id")
    char = ev.regex_dict.get("char")

    if waves_id and len(waves_id) != 9:
        return

    user_id = ruser_id(ev)
    uid = await WavesBind.get_uid_by_game(user_id, ev.bot_id)
    if not uid:
        return await bot.send(error_reply(WAVES_CODE_103))
    if not char:
        return

    im = await draw_char_score_img(ev, uid, char, user_id, waves_id)  # type: ignore
    at_sender = False
    if isinstance(im, str) and ev.group_id:
        at_sender = True
    if isinstance(im, str) or isinstance(im, bytes):
        return await bot.send(im, at_sender)


@waves_upload_char.on_regex(rf"^上传(?P<char>{PATTERN})面板图$", block=True)
async def upload_char_img(bot: Bot, ev: Event):
    char = ev.regex_dict.get("char")
    if not char:
        return
    await upload_custom_card(bot, ev, char)


@waves_char_card_list.on_regex(rf"^(?P<char>{PATTERN})面板图列表$", block=True)
async def get_char_card_list(bot: Bot, ev: Event):
    char = ev.regex_dict.get("char")
    if not char:
        return
    await get_custom_card_list(bot, ev, char)


@waves_delete_char_card.on_regex(
    rf"^删除(?P<char>{PATTERN})面板图(?P<hash_id>[a-zA-Z0-9]+)$", block=True
)
async def delete_char_card(bot: Bot, ev: Event):
    char = ev.regex_dict.get("char")
    hash_id = ev.regex_dict.get("hash_id")
    if not char or not hash_id:
        return
    await delete_custom_card(bot, ev, char, hash_id)


@waves_delete_all_card.on_regex(rf"^删除全部(?P<char>{PATTERN})面板图$", block=True)
async def delete_all_char_card(bot: Bot, ev: Event):
    char = ev.regex_dict.get("char")
    if not char:
        return
    await delete_all_custom_card(bot, ev, char)


@waves_compress_card.on_fullmatch("压缩面板图", block=True)
async def compress_char_card(bot: Bot, ev: Event):
    await compress_all_custom_card(bot, ev)