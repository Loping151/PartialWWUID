import math
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.utils import sget

from ..utils import hint
from ..utils.api.model import (
    AccountBaseInfo,
    AreaInfo,
    ExploreArea,
    ExploreItem,
    ExploreList,
)
from ..utils.error_reply import WAVES_CODE_102
from ..utils.fonts.waves_fonts import (
    waves_font_24,
    waves_font_25,
    waves_font_26,
    waves_font_30,
    waves_font_36,
    waves_font_42,
)
from ..utils.image import (
    GOLD,
    GREY,
    WAVES_FREEZING,
    WAVES_LINGERING,
    WAVES_MOLTEN,
    WAVES_MOONLIT,
    WAVES_SIERRA,
    WAVES_SINKING,
    WAVES_VOID,
    YELLOW,
    add_footer,
    change_color,
    get_waves_bg,
)
from ..utils.imagetool import draw_pic_with_ring
from ..utils.waves_api import waves_api

TEXT_PATH = Path(__file__).parent / "texture2d"

tag_yes = Image.open(TEXT_PATH / "tag_yes.png")
tag_yes_draw = ImageDraw.Draw(tag_yes)
tag_yes_draw.text((85, 30), "已完成", "white", waves_font_36, "mm")
tag_no = Image.open(TEXT_PATH / "tag_no.png")
tag_no_draw = ImageDraw.Draw(tag_no)
tag_no_draw.text((85, 30), "未完成", "white", waves_font_36, "mm")

country_color_map = {
    "黑海岸": (28, 55, 118),
    "瑝珑": (140, 113, 58),
    "黎那汐塔": (95, 52, 39),
}

progress_color = [
    (10, WAVES_MOONLIT),
    (20, WAVES_LINGERING),
    (35, WAVES_FREEZING),
    (50, WAVES_SIERRA),
    (70, WAVES_SINKING),
    (80, WAVES_VOID),
    (90, YELLOW),
    (100, WAVES_MOLTEN),
]


def get_progress_color(progress):
    float_progress = float(progress)
    result = WAVES_MOONLIT
    for _p, color in progress_color:
        if float_progress >= _p:
            result = color
    return result


async def draw_explore_img(ev: Event, uid: str, user_id: str):
    is_self_ck, ck = await waves_api.get_ck_result(uid, user_id, ev.bot_id)
    if not ck:
        return hint.error_reply(WAVES_CODE_102)
    # 账户数据
    account_info = await waves_api.get_base_info(uid, ck)
    if not account_info.success:
        return account_info.throw_msg()
    account_info = AccountBaseInfo.model_validate(account_info.data)

    explore_data = await waves_api.get_explore_data(uid, ck)
    if not explore_data.success:
        return explore_data.throw_msg()
    explore_data = ExploreList.model_validate(explore_data.data)
    if not is_self_ck and not explore_data.open:
        return hint.error_reply(msg="探索数据未开启")

    # 计算总高度
    base_info_h = 250
    footer_h = 70
    h = base_info_h + footer_h
    explore_title_h = 200
    explore_frame_h = 500

    if not explore_data.exploreList:
        return hint.error_reply(msg="探索数据为空")

    for mi, _explore in enumerate(explore_data.exploreList):
        h += explore_title_h
        if _explore.areaInfoList:
            h += math.ceil(len(_explore.areaInfoList) / 3) * explore_frame_h

    img = get_waves_bg(2000, h, "bg3")

    # 头像部分
    avatar, avatar_ring = await draw_pic_with_ring(ev)
    img.paste(avatar, (85, 70), avatar)
    img.paste(avatar_ring, (95, 80), avatar_ring)

    # 基础信息 名字 特征码
    base_info_bg = Image.open(TEXT_PATH / "base_info_bg.png")
    base_info_draw = ImageDraw.Draw(base_info_bg)
    base_info_draw.text(
        (275, 120), f"{account_info.name[:7]}", "white", waves_font_30, "lm"
    )
    base_info_draw.text(
        (226, 173), f"特征码:  {account_info.id}", GOLD, waves_font_25, "lm"
    )
    img.paste(base_info_bg, (75, 20), base_info_bg)

    # 账号基本信息，由于可能会没有，放在一起
    if account_info.is_full:
        title_bar = Image.open(TEXT_PATH / "title_bar.png")
        title_bar_draw = ImageDraw.Draw(title_bar)
        title_bar_draw.text((660, 125), "账号等级", GREY, waves_font_26, "mm")
        title_bar_draw.text(
            (660, 78), f"Lv.{account_info.level}", "white", waves_font_42, "mm"
        )

        title_bar_draw.text((810, 125), "世界等级", GREY, waves_font_26, "mm")
        title_bar_draw.text(
            (810, 78), f"Lv.{account_info.worldLevel}", "white", waves_font_42, "mm"
        )
        img.paste(title_bar, (40, 70), title_bar)

    explore_title = Image.open(TEXT_PATH / "explore_title.png")

    explore_frame = Image.open(TEXT_PATH / "explore_frame.png")
    explore_bar = Image.open(TEXT_PATH / "explore_bar.png")
    max_len = 357
    hi = base_info_h
    for mi, _explore in enumerate(explore_data.exploreList):
        _explore: ExploreArea
        _explore_title = explore_title.copy()
        _explore_title = await change_color(
            _explore_title, country_color_map.get(_explore.country.countryName, YELLOW)
        )
        # 大区域探索度
        content_img = Image.open(
            BytesIO((await sget(_explore.country.homePageIcon)).content)
        ).convert("RGBA")
        _explore_title.alpha_composite(content_img, (150, 30))
        _explore_title_draw = ImageDraw.Draw(_explore_title)
        _explore_title_draw.text(
            (370, 100), f"{_explore.country.countryName}", "white", waves_font_42, "lm"
        )
        _explore_title_draw.text(
            (370, 150),
            f"探索度: {_explore.countryProgress}%",
            "white",
            waves_font_42,
            "lm",
        )
        tag = tag_yes if float(_explore.countryProgress) == 100 else tag_no
        _explore_title.alpha_composite(tag, (1740, 60))

        img.paste(_explore_title, (0, hi), _explore_title)

        for ni, _subArea in enumerate(_explore.areaInfoList or []):
            _subArea: AreaInfo
            _explore_frame = explore_frame.copy()
            _explore_frame = await change_color(
                _explore_frame, get_progress_color(_subArea.areaProgress), h=83
            )
            _explore_frame_draw = ImageDraw.Draw(_explore_frame)

            _explore_frame_draw.text(
                (30, 50), f"{_subArea.areaName}", "white", waves_font_36, "lm"
            )
            _explore_frame_draw.text(
                (570, 50), f"{_subArea.areaProgress}%", "white", waves_font_36, "rm"
            )

            for bi, _item in enumerate(_subArea.itemList):
                _item: ExploreItem
                _explore_bar = explore_bar.copy()

                _explore_frame.alpha_composite(_explore_bar, (20, 90 + 70 * bi))
                ratio = _item.progress * 0.01
                # 进度条
                _explore_frame_draw.rounded_rectangle(
                    (131, 113 + 70 * bi, int(131 + ratio * max_len), 126 + 70 * bi),
                    radius=10,
                    fill=get_progress_color(_item.progress),
                )

                # 小地区探索度
                if len(_item.name) >= 4:
                    s = len(_item.name) // 2
                    _explore_frame_draw.text(
                        (68, 95 + 70 * bi),
                        f"{_item.name[:s]}",
                        "white",
                        waves_font_24,
                        "mm",
                    )
                    _explore_frame_draw.text(
                        (68, 125 + 70 * bi),
                        f"{_item.name[s:]}",
                        "white",
                        waves_font_24,
                        "mm",
                    )
                else:
                    _explore_frame_draw.text(
                        (68, 120 + 70 * bi),
                        f"{_item.name}",
                        "white",
                        waves_font_30,
                        "mm",
                    )
                _explore_frame_draw.text(
                    (580, 120 + 70 * bi),
                    f"{_item.progress}%",
                    "white",
                    waves_font_30,
                    "rm",
                )

            _w = 100 + 600 * (ni % 3)
            _h = hi + explore_title_h + explore_frame_h * int(ni / 3)
            img.alpha_composite(_explore_frame, (_w, _h))

        hi += (
            math.ceil(len(_explore.areaInfoList or []) / 3) * explore_frame_h
            + explore_title_h
        )

    img = add_footer(img)
    img = await convert_img(img)
    return img
