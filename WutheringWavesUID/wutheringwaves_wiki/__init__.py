import re

from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.sv import SV

from ..utils.name_convert import char_name_to_char_id
from .draw_char import draw_char_wiki
from .draw_echo import draw_wiki_echo
from .draw_list import draw_sonata_list, draw_weapon_list
from .draw_weapon import draw_wiki_weapon
from .guide import get_guide

sv_waves_guide = SV("鸣潮攻略")
sv_waves_wiki = SV("鸣潮wiki")


@sv_waves_guide.on_regex(
    r"^[\u4e00-\u9fa5]+(?:共鸣链|命座|天赋|技能|图鉴|wiki|介绍)$", block=True
)
async def send_waves_wiki(bot: Bot, ev: Event):
    match = re.search(
        r"(?P<wiki_name>[\u4e00-\u9fa5]+)(?P<wiki_type>共鸣链|命座|天赋|技能|图鉴|wiki|介绍)",
        ev.raw_text,
    )
    if not match:
        return
    ev.regex_dict = match.groupdict()
    wiki_name = ev.regex_dict.get("wiki_name", "")
    wiki_type = ev.regex_dict.get("wiki_type")

    at_sender = True if ev.group_id else False
    if wiki_type in ("共鸣链", "命座", "天赋", "技能"):
        char_name = wiki_name
        char_id = char_name_to_char_id(char_name)
        if not char_id:
            msg = f"[鸣潮] wiki【{char_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
            return await bot.send(msg, at_sender)

        query_role_type = (
            "天赋" if "技能" in wiki_type or "天赋" in wiki_type else "命座"
        )
        img = await draw_char_wiki(char_id, query_role_type)
        if isinstance(img, str):
            msg = f"[鸣潮] wiki【{wiki_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
            return await bot.send(msg, at_sender)
        await bot.send(img)
    else:
        img = await draw_wiki_weapon(wiki_name)
        if isinstance(img, str) or not img:
            echo_name = wiki_name
            await bot.logger.info(f"[鸣潮] 开始获取{echo_name}wiki")
            img = await draw_wiki_echo(echo_name)

        if isinstance(img, str) or not img:
            msg = f"[鸣潮] wiki【{wiki_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
            return await bot.send(msg, at_sender)

        await bot.send(img)


@sv_waves_guide.on_regex(r"[\u4e00-\u9fa5]+攻略$", block=True)
async def send_role_guide_pic(bot: Bot, ev: Event):
    match = re.search(r"(?P<char>[\u4e00-\u9fa5]+)攻略", ev.raw_text)
    if not match:
        return
    ev.regex_dict = match.groupdict()

    char_name = ev.regex_dict.get("char", "")
    char_id = char_name_to_char_id(char_name)
    at_sender = True if ev.group_id else False
    if not char_id:
        msg = f"[鸣潮] 角色名【{char_name}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
        return await bot.send(msg, at_sender)

    await get_guide(bot, ev, char_name)


@sv_waves_guide.on_regex(r"([\u4e00-\u9fa5]+)?武器(列表)?$", block=True)
async def send_weapon_list(bot: Bot, ev: Event):
    match = re.search(r"(?P<type>[\u4e00-\u9fa5]+)?武器(列表)?$", ev.raw_text)
    if not match:
        return
    ev.regex_dict = match.groupdict()
    weapon_type = ev.regex_dict.get("type", "")
    img = await draw_weapon_list(weapon_type)
    await bot.send(img)


@sv_waves_guide.on_regex(r".*套装(列表)?$", block=True)
async def send_sonata_list(bot: Bot, ev: Event):
    await bot.send(await draw_sonata_list())
