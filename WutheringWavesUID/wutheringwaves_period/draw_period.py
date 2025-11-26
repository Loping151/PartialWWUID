import asyncio
from pathlib import Path
from typing import Any, Dict, Optional, Union

from PIL import Image, ImageDraw

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.sv import get_plugin_available_prefix
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.api.model import AccountBaseInfo, Period, PeriodDetail, PeriodList
from ..utils.database.models import WavesBind
from ..utils.fonts.waves_fonts import (
    waves_font_24,
    waves_font_30,
    waves_font_36,
)
from ..utils.image import add_footer, get_event_avatar, get_waves_bg
from ..utils.waves_api import waves_api

TEXT_PATH = Path(__file__).parent / "texture2d"


based_w = 750
based_h = 930

# 定义颜色列表
colors = [
    (255, 102, 102),  # 红色 - 玩法奖励
    (255, 153, 51),  # 橙色 - 活动奖励
    (255, 206, 84),  # 黄色 - 日常挑战
    (75, 192, 192),  # 青色 - 大世界探索
    (144, 238, 144),  # 绿色 - 任务获取
    (54, 162, 235),  # 蓝色 - 其他
]

MSG_TOKEN = "特征码登录已全部失效！请使用【{}登录】完成绑定！"
MSG_TOKEN_EXPIRED = "该特征码[{}]登录已失效！请使用【{}登录】完成绑定！"
MSG_NO_PERIOD = "该特征码[{}]没有[{}]简报数据~"
PREFIX = get_plugin_available_prefix("WutheringWavesUID")


async def process_uid(
    uid, ev, period_param: Optional[Union[int, str]]
) -> Optional[Union[Dict[str, Any], str]]:
    ck = await waves_api.get_self_waves_ck(uid, ev.user_id, ev.bot_id)
    if not ck:
        return None

    period_list = await waves_api.get_period_list(uid, ck)
    if not period_list.success or not period_list.data:
        return None

    period_list = PeriodList.model_validate(period_list.data)

    period_type = "month"
    period_node: Optional[Period] = None
    if period_param:
        for period in period_list.months:
            if period.index == period_param or period.title == period_param:
                period_node = period
                period_type = "month"
                break
        for period in period_list.weeks:
            if period.index == period_param or period.title == period_param:
                period_node = period
                period_type = "week"
                break
        for period in period_list.versions:
            if period.index == period_param or period.title == period_param:
                period_node = period
                period_type = "version"
                break
    elif period_list.versions:
        period_list.versions.sort(key=lambda x: x.index, reverse=True)
        period_node = period_list.versions[0]
        period_type = "version"

    if not period_node:
        return MSG_NO_PERIOD.format(uid, period_param)

    period_detail = await waves_api.get_period_detail(
        period_type, period_node.index, uid, ck
    )
    if not period_detail.success or not period_detail.data:
        return None
    period_detail = PeriodDetail.model_validate(period_detail.data)

    account_info = await waves_api.get_base_info(uid, ck)
    if not account_info.success or not account_info.data:
        return None
    account_info = AccountBaseInfo.model_validate(account_info.data)

    return {
        "period_node": period_node,
        "period_detail": period_detail,
        "account_info": account_info,
    }


async def draw_period_img(bot: Bot, ev: Event):
    period_param = ev.text.strip() if ev.text else None
    logger.info(f"[鸣潮][资源简报]绘图开始: {period_param}")
    try:
        uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)

        if uid_list is None:
            return MSG_TOKEN.format(PREFIX)

        # 进行校验UID是否绑定CK
        tasks = [process_uid(uid, ev, period_param) for uid in uid_list]
        results = await asyncio.gather(*tasks)

        # 过滤掉 None 值
        valid_period_list = [res for res in results if isinstance(res, dict)]

        if len(valid_period_list) == 0:
            msg = [res for res in results if isinstance(res, str)]
            if msg:
                return "\n".join(msg)
            return MSG_TOKEN.format(PREFIX)

        # 开始绘图任务
        task = []
        img = Image.new(
            "RGBA", (based_w, based_h * len(valid_period_list)), (0, 0, 0, 0)
        )
        for uid_index, valid in enumerate(valid_period_list):
            task.append(_draw_all_period_img(ev, img, valid, uid_index))
        await asyncio.gather(*task)
        res = await convert_img(img)
    except TypeError:
        logger.exception("[鸣潮][资源简报]绘图失败!")
        res = "你绑定过的UID中可能存在过期CK~请重新绑定一下噢~"

    return res


async def _draw_all_period_img(
    ev: Event, img: Image.Image, valid: Dict[str, Any], uid_index: int
):
    period_img = await _draw_period_img(ev, valid)
    period_img = period_img.convert("RGBA")
    img.paste(period_img, (0, based_h * uid_index), period_img)


async def _draw_period_img(ev: Event, valid: Dict):
    period_detail: PeriodDetail = valid["period_detail"]
    account_info: AccountBaseInfo = valid["account_info"]
    period_node: Period = valid["period_node"]

    img = get_waves_bg(based_w, based_h, bg="bg10")

    # 遮罩
    mask_img = Image.open(TEXT_PATH / "home-mask-black.png").convert("RGBA")
    mask_img = mask_img.crop((0, 0, based_w, based_h - 100))
    img.alpha_composite(mask_img, (0, 70))

    # 绘制角色信息 750 × 206
    title_img = Image.open(TEXT_PATH / "top-bg.png")
    title_img_draw = ImageDraw.Draw(title_img)
    title_img_draw.text((240, 75), f"{account_info.name}", "black", waves_font_36, "lm")
    title_img_draw.text(
        (240, 140), f"特征码: {account_info.id}", "black", waves_font_24, "lm"
    )

    avatar_img = await draw_pic_with_ring(ev)
    title_img.paste(avatar_img, (27, 8), avatar_img)

    img.paste(title_img, (0, 30), title_img)

    # 绘制slagon.png
    slagon_img = Image.open(TEXT_PATH / "slagon.png")
    img.paste(slagon_img, (500, 95), slagon_img)

    # 绘制底板
    home_bg = await crop_home_img()
    # topup
    topup_bg = Image.open(TEXT_PATH / "txt-topup.png")
    home_bg.alpha_composite(topup_bg, (0, 60))

    # ico-sourct-tab.png
    icon_source_tab = Image.open(TEXT_PATH / "ico-sourct-tab.png")
    icon_souce_tab_draw = ImageDraw.Draw(icon_source_tab)
    icon_souce_tab_draw.text(
        (77, 25), f"{period_node.title}", "white", waves_font_30, "mm"
    )
    home_bg.paste(icon_source_tab, (500, 60), icon_source_tab)

    # 绘制tab
    star_tab = Image.open(TEXT_PATH / "tab-star-bg.png")
    star_tab_draw = ImageDraw.Draw(star_tab)
    star_tab_draw.text((120, 35), "星声", "black", waves_font_24, "lm")
    star_tab_draw.text(
        (120, 80), f"{period_detail.totalStar}", "black", waves_font_30, "lm"
    )
    coin_tab = Image.open(TEXT_PATH / "tab-coin-bg.png")
    coin_tab_draw = ImageDraw.Draw(coin_tab)
    coin_tab_draw.text((120, 30), "贝币", "black", waves_font_24, "lm")
    coin_tab_draw.text(
        (120, 80), f"{period_detail.totalCoin}", "black", waves_font_30, "lm"
    )

    home_bg.paste(star_tab, (40, 115), star_tab)
    home_bg.paste(coin_tab, (380, 115), coin_tab)

    # source
    source_bg = Image.open(TEXT_PATH / "txt-source.png")
    home_bg.alpha_composite(source_bg, (0, 270))

    # 饼图数据
    pie_data = {
        item.type: (
            float(item.num / period_detail.totalStar * 100)
            if period_detail.totalStar
            else 0
        )
        for item in period_detail.starList
    }
    pie_data_num_map = {item.type: item.num for item in period_detail.starList}

    # 获取合成后的饼图
    pie_placeholder = create_pie_chart_with_placeholder(pie_data)
    home_bg.paste(pie_placeholder, (380, 320), pie_placeholder)

    # 在左侧绘制图例
    draw_legend_on_home_bg(home_bg, pie_data_num_map, 50, 345)

    img.paste(home_bg, (30, 235), home_bg)
    img = add_footer(img, 600, 25)
    return img


async def crop_home_img():
    img = Image.new("RGBA", (718, 650), (0, 0, 0, 0))
    # 绘制底板
    # 718*56
    home_main_1 = Image.open(TEXT_PATH / "home-main-p1.png")
    img.paste(home_main_1, (0, 0), home_main_1)

    # 718*280
    home_main_2 = Image.open(TEXT_PATH / "home-main-p2.png")
    img.paste(home_main_2, (0, 56), home_main_2)

    home_main_2_1 = Image.open(TEXT_PATH / "home-main-p2.png")
    home_main_2_1 = home_main_2_1.crop((0, 0, 718, 230))
    img.paste(home_main_2_1, (0, 336), home_main_2_1)

    # 718*86
    home_main_3 = Image.open(TEXT_PATH / "home-main-p3.png")
    img.paste(home_main_3, (0, 566), home_main_3)

    return img


async def draw_pic_with_ring(ev: Event):
    pic = await get_event_avatar(ev, is_valid_at_param=False)

    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    img = Image.new("RGBA", (200, 200))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    img.paste(resize_pic, (20, 20), mask)

    return img


def draw_legend_on_home_bg(
    home_bg: Image.Image,
    pie_data_num_map: Dict[str, int],
    x: int,
    y: int,
):
    draw = ImageDraw.Draw(home_bg)

    for i, (label, value) in enumerate(pie_data_num_map.items()):
        current_y = y + i * 45

        # 绘制颜色圆点
        color = colors[i % len(colors)]
        draw.ellipse([x + 5, current_y + 5, x + 20, current_y + 20], fill=color)

        # 绘制标签
        # percentage = f"{value:.1f}%"
        percentage = f"{value}"
        draw.text((x + 30, current_y + 2), label, fill=(80, 80, 80), font=waves_font_24)
        draw.text((x + 170, current_y + 2), percentage, fill=color, font=waves_font_24)


def draw_pie_chart_for_bg(
    data_dict: Dict[str, float], bg_size: int, outer_radius: int, inner_radius: int
) -> Image.Image:
    # 创建透明背景的图片
    img = Image.new("RGBA", (bg_size, bg_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 计算总值
    total = sum(data_dict.values())
    if total == 0:
        return img

    # 计算圆的边界框
    center = bg_size // 2
    outer_bbox = [
        center - outer_radius,
        center - outer_radius,
        center + outer_radius,
        center + outer_radius,
    ]
    inner_bbox = [
        center - inner_radius,
        center - inner_radius,
        center + inner_radius,
        center + inner_radius,
    ]

    # 绘制饼图
    start_angle = -90  # 从顶部开始
    color_index = 0

    for label, value in data_dict.items():
        # 计算角度
        angle = (value / total) * 360
        end_angle = start_angle + angle

        # 绘制扇形
        if angle > 0:
            # 先绘制外圆扇形
            draw.pieslice(
                outer_bbox,
                start_angle,
                end_angle,
                fill=colors[color_index % len(colors)],
                outline=(255, 255, 255, 100),
                width=1,
            )

            # 再绘制内圆来创建圆环效果（使用透明色覆盖）
            draw.pieslice(
                inner_bbox,
                start_angle,
                end_angle,
                fill=(255, 255, 255, 0),  # 透明
            )

        start_angle = end_angle
        color_index += 1

    # 最后绘制内圆的边框
    draw.ellipse(inner_bbox, fill=None, outline=(255, 255, 255, 100), width=1)

    return img


def create_pie_chart_with_placeholder(pie_data: Dict[str, float]) -> Image.Image:
    # 加载placeholder背景图
    placeholder = Image.open(TEXT_PATH / "placeholder.png").convert("RGBA")

    # 计算外圆和内圆的半径（根据背景图的比例）
    outer_radius = 120
    inner_radius = 45

    # 创建饼图，使其完全匹配placeholder的圆环
    pie_chart = draw_pie_chart_for_bg(pie_data, 300, outer_radius, inner_radius)

    # 将饼图合成到placeholder上
    placeholder.alpha_composite(pie_chart, (10, 5))

    return placeholder
