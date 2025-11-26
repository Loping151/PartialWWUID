from pathlib import Path

from PIL import Image, ImageDraw

from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.api.model import AccountBaseInfo, MoreActivity
from ..utils.error_reply import WAVES_CODE_102
from ..utils.fonts.waves_fonts import (
    waves_font_25,
    waves_font_26,
    waves_font_30,
    waves_font_42,
)
from ..utils.hint import error_reply
from ..utils.image import (
    GOLD,
    GREY,
    add_footer,
    get_waves_bg,
    pic_download_from_url,
)
from ..utils.imagetool import draw_pic_with_ring
from ..utils.resource.RESOURCE_PATH import POKER_PATH
from ..utils.waves_api import waves_api

TEXT_PATH = Path(__file__).parent / "texture2d"
POKER_ERROR = "数据获取失败，请稍后再试"

lock_img = Image.open(TEXT_PATH / "lock.png")
lock_resized = lock_img.resize((40, 40))

# 将锁图标转换为白色
lock_white = Image.new("RGBA", lock_resized.size, (255, 255, 255, 0))
for x in range(lock_resized.width):
    for y in range(lock_resized.height):
        pixel = lock_resized.getpixel((x, y))
        if isinstance(pixel, tuple) and len(pixel) >= 4:
            r, g, b, a = pixel[:4]
            if a > 0:  # 只处理不透明的像素
                lock_white.putpixel((x, y), (255, 255, 255, a))  # 白色，保持原透明度


def draw_rounded_rectangle(draw, coords, radius, fill=None, outline=None, width=1):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = coords
    draw.rounded_rectangle(
        coords, radius=radius, fill=fill, outline=outline, width=width
    )


def draw_progress_bar(
    draw,
    x,
    y,
    width,
    height,
    progress,
    max_progress,
    bg_color=(60, 60, 60),
    fill_color=(255, 215, 0),
):
    """绘制进度条"""
    # 背景
    draw_rounded_rectangle(
        draw, (x, y, x + width, y + height), radius=height // 2, fill=bg_color
    )

    # 进度
    if max_progress > 0:
        progress_width = int((progress / max_progress) * width)
        if progress_width > 0:
            draw_rounded_rectangle(
                draw,
                (x, y, x + progress_width, y + height),
                radius=height // 2,
                fill=fill_color,
            )


async def draw_poker_img(ev: Event, uid: str, user_id: str):
    is_self_ck, ck = await waves_api.get_ck_result(uid, user_id, ev.bot_id)
    if not ck:
        return error_reply(WAVES_CODE_102)

    moreActivity = await waves_api.get_more_activity(uid, ck)
    if not moreActivity.success:
        return moreActivity.throw_msg()

    temp: MoreActivity = MoreActivity.model_validate(moreActivity.data)
    phantomBattle = temp.phantomBattle

    # 账户数据
    account_info = await waves_api.get_base_info(uid, ck)
    if not account_info.success:
        return account_info.throw_msg()
    account_info = AccountBaseInfo.model_validate(account_info.data)

    # 计算徽章行数来调整总高度
    total_badges = len(phantomBattle.badgeList)
    badges_per_row = 4
    badge_rows = (total_badges + badges_per_row - 1) // badges_per_row
    badge_section_height = badge_rows * 220 + 150

    h = 720 + badge_section_height + 50  # 基础高度 + 徽章区域高度
    card_img = get_waves_bg(1000, h, "bg11")

    # 绘制个人信息
    base_info_bg = Image.open(TEXT_PATH / "base_info_bg.png")
    base_info_draw = ImageDraw.Draw(base_info_bg)
    base_info_draw.text(
        (275, 120), f"{account_info.name[:7]}", "white", waves_font_30, "lm"
    )
    base_info_draw.text(
        (226, 173), f"特征码:  {account_info.id}", GOLD, waves_font_25, "lm"
    )
    card_img.paste(base_info_bg, (15, 20), base_info_bg)

    # 头像 头像环
    avatar, avatar_ring = await draw_pic_with_ring(ev)
    card_img.paste(avatar, (25, 70), avatar)
    card_img.paste(avatar_ring, (35, 80), avatar_ring)

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
        card_img.paste(title_bar, (-20, 70), title_bar)

    y_offset = 270

    phantom_info_bg = Image.new("RGBA", (970, 430), (0, 0, 0, 0))
    phantom_info_draw = ImageDraw.Draw(phantom_info_bg)

    # 卡片背景
    draw_rounded_rectangle(
        phantom_info_draw,
        (0, 0, 970, 230),
        radius=12,
        fill=(60, 60, 60, 200),
        outline=(100, 100, 100),
        width=2,
    )

    # 标题
    phantom_info_draw.text((30, 45), "决斗家信息", GOLD, waves_font_30, "lm")

    # 上方卡片：等级信息
    level_card_bg = Image.new("RGBA", (970, 180), (0, 0, 0, 0))
    level_card_draw = ImageDraw.Draw(level_card_bg)

    # 等级数字
    level_bg = Image.open(TEXT_PATH / "level_bg.png")
    level_bg_draw = ImageDraw.Draw(level_bg)
    level_bg_draw.text(
        (78, 75),
        f"{phantomBattle.level}",
        "white",
        waves_font_42,
        "mm",
    )
    level_card_bg.paste(level_bg, (30, 10), level_bg)

    # 右侧等级信息
    level_text_x = 210
    level_card_draw.text(
        (level_text_x, 75), phantomBattle.levelName, "white", waves_font_26, "lm"
    )

    # 经验进度条
    draw_progress_bar(
        level_card_draw,
        level_text_x,
        120,
        680,
        12,
        phantomBattle.exp,
        phantomBattle.expLimit,
        bg_color=(40, 40, 40),
        fill_color=GOLD,
    )

    # 经验数值显示在右侧
    exp_text = f"{phantomBattle.exp}/{phantomBattle.expLimit}"
    level_card_draw.text((870, 75), exp_text, GOLD, waves_font_25, "rm")

    # 粘贴等级卡片
    phantom_info_bg.paste(level_card_bg, (0, 60), level_card_bg)

    # 下方卡片：卡片收集信息
    card_card_bg = Image.new("RGBA", (970, 180), (0, 0, 0, 0))
    card_card_draw = ImageDraw.Draw(card_card_bg)

    # 卡片背景
    draw_rounded_rectangle(
        card_card_draw,
        (0, 0, 970, 180),
        radius=12,
        fill=(60, 60, 60, 200),
        outline=(100, 100, 100),
        width=2,
    )

    card_bg = Image.open(TEXT_PATH / "card_bg.png")
    card_card_bg.paste(card_bg, (30, 10), card_bg)

    # 右侧卡片信息
    card_text_x = 210
    card_card_draw.text(
        (card_text_x, 75), "已收集卡片数量", "white", waves_font_26, "lm"
    )

    # 卡片进度条
    draw_progress_bar(
        card_card_draw,
        card_text_x,
        120,
        680,
        12,
        phantomBattle.cardNum,
        phantomBattle.maxCardNum,
        bg_color=(40, 40, 40),
        fill_color=GOLD,
    )

    # 卡片数值显示在右侧
    card_text = f"{phantomBattle.cardNum}/{phantomBattle.maxCardNum}"
    card_card_draw.text((870, 75), card_text, GOLD, waves_font_25, "rm")

    # 粘贴卡片收集卡片
    phantom_info_bg.paste(card_card_bg, (0, 250), card_card_bg)

    card_img.paste(phantom_info_bg, (15, y_offset), phantom_info_bg)

    # 绘制徽章图鉴部分
    y_offset += 450  # 调整间距

    # 徽章图鉴背景
    badge_bg = Image.new("RGBA", (970, badge_section_height), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge_bg)

    # 背景框架
    draw_rounded_rectangle(
        badge_draw,
        (0, 0, 970, badge_section_height),
        radius=12,
        fill=(40, 40, 40, 220),
        outline=(80, 80, 80),
        width=2,
    )

    # 标题
    badge_draw.text((30, 50), "徽章图鉴", GOLD, waves_font_30, "lm")
    badge_draw.text(
        (30, 105),
        f"已收集徽章：{phantomBattle.badgeNum}/{phantomBattle.maxBadgeNum}",
        GREY,
        waves_font_25,
        "lm",
    )

    # 收集进度条
    collection_progress_x, collection_progress_y = 270, 100
    collection_progress_width = 500
    draw_progress_bar(
        badge_draw,
        collection_progress_x,
        collection_progress_y,
        collection_progress_width,
        8,
        phantomBattle.badgeNum,
        phantomBattle.maxBadgeNum,
        bg_color=(60, 60, 60),
        fill_color=(255, 100, 100),
    )

    # 绘制徽章网格 - 增加顶部间距
    badge_start_y = 150
    badge_size = 180
    badges_per_row = 4
    badge_spacing = 40

    for i, badge in enumerate(phantomBattle.badgeList):
        row = i // badges_per_row
        col = i % badges_per_row

        badge_x = 60 + col * (badge_size + badge_spacing)
        badge_y = badge_start_y + row * (badge_size + badge_spacing)

        # 徽章背景
        badge_item_bg = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
        badge_item_draw = ImageDraw.Draw(badge_item_bg)

        if badge.unlock:
            # 已解锁的徽章 - 金色背景框
            draw_rounded_rectangle(
                badge_item_draw,
                (0, 0, badge_size, badge_size),
                radius=15,
                fill=(120, 100, 50, 200),
                outline=(255, 215, 0),
                width=3,
            )

        else:
            # 未解锁的徽章 - 灰色背景
            draw_rounded_rectangle(
                badge_item_draw,
                (0, 0, badge_size, badge_size),
                radius=15,
                fill=(60, 60, 60, 200),
                outline=(100, 100, 100),
                width=2,
            )

        icon_img = await pic_download_from_url(POKER_PATH, pic_url=badge.iconUrl)

        if icon_img:
            # 图标区域
            icon_area_size = 120
            icon_area_x = (badge_size - icon_area_size) // 2
            icon_area_y = 20

            # 调整图标尺寸
            if icon_img.size != (icon_area_size, icon_area_size):
                icon_img = icon_img.resize(
                    (icon_area_size, icon_area_size), Image.Resampling.LANCZOS
                )

            # 创建圆形遮罩
            mask = Image.new("L", (icon_area_size, icon_area_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, icon_area_size, icon_area_size), fill=255)

            # 如果未解锁，对图标应用灰度效果
            if not badge.unlock:
                icon_img = icon_img.convert("L").convert("RGBA")
                # 降低透明度
                icon_img.putalpha(120)

            # 应用圆形遮罩
            icon_bg = Image.new(
                "RGBA", (icon_area_size, icon_area_size), (255, 255, 255, 0)
            )
            icon_bg.paste(icon_img, (0, 0))

            badge_item_bg.paste(icon_bg, (icon_area_x, icon_area_y), mask)

            # 如果未解锁，添加白色锁图标覆盖
            if not badge.unlock:
                lock_x = icon_area_x + (icon_area_size - 40) // 2
                lock_y = icon_area_y + (icon_area_size - 40) // 2
                badge_item_bg.paste(lock_white, (lock_x, lock_y), lock_white)

        text_color = "white" if badge.unlock else GREY

        # 名称背景
        name_bg_y = badge_size - 45
        draw_rounded_rectangle(
            badge_item_draw,
            (5, name_bg_y, badge_size - 5, badge_size - 5),
            radius=8,
            fill=(0, 0, 0, 180),
        )

        badge_item_draw.text(
            (badge_size // 2, badge_size - 25),
            badge.name,
            text_color,
            waves_font_25,
            "mm",
        )

        badge_bg.paste(badge_item_bg, (badge_x, badge_y), badge_item_bg)

    card_img.paste(badge_bg, (15, y_offset), badge_bg)

    card_img = add_footer(card_img, 600, 20)
    card_img = await convert_img(card_img)
    return card_img
