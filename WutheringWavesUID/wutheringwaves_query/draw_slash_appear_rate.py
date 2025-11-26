from pathlib import Path
from typing import Dict, List, Union

import httpx
from PIL import Image, ImageDraw

from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.api.wwapi import GET_SLASH_APPEAR_RATE
from ..utils.ascension.char import get_char_model
from ..utils.ascension.model import CharacterModel
from ..utils.fonts.waves_fonts import (
    waves_font_20,
    waves_font_30,
    waves_font_40,
    waves_font_58,
)
from ..utils.image import add_footer, get_ICON, get_square_avatar, get_waves_bg
from ..utils.resource.constant import NAME_ALIAS
from ..utils.util import timed_async_cache

TEXT_PATH = Path(__file__).parent / "texture2d"


@timed_async_cache(expiration=3600, condition=lambda x: isinstance(x, dict))
async def get_slash_appear_rate_data() -> Union[Dict, None]:
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(
                GET_SLASH_APPEAR_RATE,
                headers={
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(10),
            )
            if res.status_code == 200:
                return res.json().get("data", [])
        except Exception as e:
            logger.exception(f"获取冥海出场率数据失败: {e}")


async def draw_slash_use_rate(ev: Event):
    data = await get_slash_appear_rate_data()
    if not data:
        return "暂无冥海出场率数据, 请稍后再试"

    filter_type = None
    text = ev.text.strip() if ev.text else ""
    if "总" in text or "全" in text or "总" in ev.command:
        filter_type = "all"
    elif "上半" in text or "上" in text or "一" in text or "1" in text:
        filter_type = "1"
    elif "下半" in text or "下" in text or "二" in text or "2" in text:
        filter_type = "2"

    defaule_filter = 4
    title_h = 500
    bar_star_h = 180
    slash_name_bg_h = 150
    footer_h = 50

    if filter_type is None:
        show_data = data["half_rate_list"]

        totalNum = defaule_filter * 2
        h = title_h + totalNum * bar_star_h + slash_name_bg_h * 2 + footer_h

    elif "1" == filter_type:
        show_data = []
        show_data.append(data["half_rate_list"][0])

        char_num = len(data["half_rate_list"][0]["rates"])
        totalNum = char_num // 4 + (0 if char_num % 4 == 0 else 1)

        h = title_h + totalNum * bar_star_h + slash_name_bg_h + footer_h

    elif "2" == filter_type:
        show_data = []
        show_data.append(data["half_rate_list"][1])

        char_num = len(data["half_rate_list"][1]["rates"])
        totalNum = char_num // 4 + (0 if char_num % 4 == 0 else 1)

        h = title_h + totalNum * bar_star_h + slash_name_bg_h + footer_h
    else:
        show_data = data["appear_rate_list"]

        char_num = len(data["appear_rate_list"][0]["rates"])
        totalNum = char_num // 4 + (0 if char_num % 4 == 0 else 1)

        h = title_h + totalNum * bar_star_h + slash_name_bg_h + footer_h

    card_img = get_waves_bg(1050, h, "bg9")

    # title
    title_bg = Image.open(TEXT_PATH / "slash.jpg")
    title_bg = title_bg.crop((0, 0, 1050, 500))

    # icon
    icon = get_ICON()
    icon = icon.resize((128, 128))
    title_bg.paste(icon, (60, 240), icon)

    # title
    title_text = "#冥歌海墟出场率"
    title_bg_draw = ImageDraw.Draw(title_bg)
    title_bg_draw.text((220, 290), title_text, "white", waves_font_58, "lm")

    # 遮罩
    char_mask = Image.open(TEXT_PATH / "char_mask.png").convert("RGBA")
    char_mask_temp = Image.new("RGBA", char_mask.size, (0, 0, 0, 0))
    char_mask_temp.paste(title_bg, (0, 0), char_mask)

    card_img.paste(char_mask_temp, (0, 0), char_mask_temp)

    # 深塔出场率
    start_y = 470

    for index, i in enumerate(show_data):
        rates: List[Dict] = i["rates"]

        slash_name_bg = Image.open(TEXT_PATH / "difficulty_2.png")
        slash_name_bg_draw = ImageDraw.Draw(slash_name_bg)
        if len(show_data) == 1:
            text = "无尽湍渊 - 总数据"
        else:
            text = "无尽湍渊 - 上半" if index == 0 else "无尽湍渊 -下半"

        if filter_type == "1":
            text = "无尽湍渊 - 上半"
        elif filter_type == "2":
            text = "无尽湍渊 - 下半"

        slash_name_bg_draw.text(
            (140, 60),
            text,
            "white",
            waves_font_40,
            "lm",
        )

        card_img.alpha_composite(slash_name_bg, (25, start_y))

        start_y += slash_name_bg_h

        for rIndex, rate_temp in enumerate(rates):
            char_id = rate_temp["char_id"]
            rate = rate_temp["rate"]
            char_model = get_char_model(char_id)
            if not char_model:
                continue

            temp_pic = await get_temp_pic(char_id, char_model, rate)
            temp_pic = temp_pic.resize((200, 157))
            card_img.alpha_composite(
                temp_pic,
                (
                    50 + 240 * (rIndex % 4),
                    start_y + (rIndex // 4) * 180,
                ),
            )

            if filter_type is None and rIndex >= defaule_filter * 4 - 1:
                break

        if filter_type is None:
            start_y += 180 * defaule_filter

    card_img = add_footer(card_img)
    card_img = await convert_img(card_img)
    return card_img


async def get_temp_pic(char_id: str, char_model: CharacterModel, rate: float):
    avatar = await get_square_avatar(char_id)
    avatar = avatar.resize((180, 180))
    if char_model.starLevel == 5:
        star_fg = Image.open(TEXT_PATH / "star5_fg.png")
        star_bg = Image.open(TEXT_PATH / "star5_bg.png")
    else:
        star_fg = Image.open(TEXT_PATH / "star4_fg.png")
        star_bg = Image.open(TEXT_PATH / "star4_bg.png")

    star_bg_temp = Image.new("RGBA", star_bg.size)
    star_bg_temp.paste(star_bg, (0, 0))
    star_bg_temp.alpha_composite(avatar, (80, -10))

    char_name = NAME_ALIAS.get(char_model.name, char_model.name)
    if len(char_name) <= 2:
        name_bg = Image.new("RGBA", (60, 25), color=(255, 255, 255, 0))
        rank_draw = ImageDraw.Draw(name_bg)
        rank_draw.rectangle([0, 0, 60, 25], fill=(255, 255, 255) + (int(0.9 * 255),))
        rank_draw.text((30, 12), f"{char_name}", "black", waves_font_20, "mm")
    else:
        name_bg = Image.new("RGBA", (80, 25), color=(255, 255, 255, 0))
        rank_draw = ImageDraw.Draw(name_bg)
        rank_draw.rectangle([0, 0, 80, 25], fill=(255, 255, 255) + (int(0.9 * 255),))
        rank_draw.text((40, 12), f"{char_name}", "black", waves_font_20, "mm")

    temp_img = Image.new("RGBA", (256, 200), color=(0, 0, 0, 60))

    temp_img.paste(star_bg_temp, (0, 0))
    temp_img.alpha_composite(star_fg, (0, 0))
    temp_img.alpha_composite(name_bg, (10, 110))
    temp_draw = ImageDraw.Draw(temp_img)
    temp_draw.text((125, 180), f"{rate:.2%}", "white", waves_font_30, "mm")

    return temp_img
