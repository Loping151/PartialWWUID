import asyncio
import copy
from pathlib import Path
from typing import Optional, Union

import httpx
from PIL import Image, ImageDraw

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.api.wwapi import (
    GET_TOTAL_RANK_URL,
    TotalRankRequest,
    TotalRankResponse,
)
from ..utils.cache import TimedCache
from ..utils.database.models import WavesBind
from ..utils.fonts.waves_fonts import (
    waves_font_12,
    waves_font_16,
    waves_font_18,
    waves_font_20,
    waves_font_28,
    waves_font_30,
    waves_font_34,
    waves_font_58,
)
from ..utils.image import (
    AMBER,
    GREY,
    RED,
    SPECIAL_GOLD,
    WAVES_FREEZING,
    WAVES_LINGERING,
    WAVES_MOLTEN,
    WAVES_MOONLIT,
    WAVES_SIERRA,
    WAVES_VOID,
    add_footer,
    get_ICON,
    get_qq_avatar,
    get_square_avatar,
    get_waves_bg,
)
from ..utils.util import get_version
from ..wutheringwaves_config import WutheringWavesConfig

TEXT_PATH = Path(__file__).parent / "texture2d"
avatar_mask = Image.open(TEXT_PATH / "avatar_mask.png")
char_mask = Image.open(TEXT_PATH / "char_mask.png")
pic_cache = TimedCache(600, 200)


BOT_COLOR = [
    WAVES_MOLTEN,
    AMBER,
    WAVES_VOID,
    WAVES_SIERRA,
    WAVES_FREEZING,
    WAVES_LINGERING,
    WAVES_MOONLIT,
]


async def get_rank(item: TotalRankRequest) -> Optional[TotalRankResponse]:
    WavesToken = WutheringWavesConfig.get_config("WavesToken").data

    if not WavesToken:
        return

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                GET_TOTAL_RANK_URL,
                json=item.dict(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {WavesToken}",
                },
                timeout=httpx.Timeout(10),
            )
            if res.status_code == 200:
                return TotalRankResponse.model_validate(res.json())
            else:
                logger.warning(f"获取练度排行失败: {res.status_code} - {res.text}")
        except Exception as e:
            logger.exception(f"获取练度排行失败: {e}")


async def draw_total_rank(bot: Bot, ev: Event, pages: int) -> Union[str, bytes]:
    page_num = 20
    self_uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
    if not self_uid:
        self_uid = ""
    item = TotalRankRequest(
        page=pages,
        page_num=page_num,
        waves_id=self_uid,
        version=get_version(dynamic=True, waves_id=self_uid, pages=pages),
    )

    rankInfoList = await get_rank(item)
    if not rankInfoList:
        return "获取练度总排行失败"

    if rankInfoList.message and not rankInfoList.data:
        return rankInfoList.message

    if not rankInfoList.data:
        return "获取练度总排行失败"

    # 设置图像尺寸
    width = 1300
    text_bar_height = 130
    item_spacing = 120
    header_height = 510
    footer_height = 50
    char_list_len = len(rankInfoList.data.score_details)

    # 计算所需的总高度
    total_height = (
        header_height + text_bar_height + item_spacing * char_list_len + footer_height
    )

    # 创建带背景的画布 - 使用bg9
    card_img = get_waves_bg(width, total_height, "bg9")

    text_bar_img = Image.new("RGBA", (width, 130), color=(0, 0, 0, 0))
    text_bar_draw = ImageDraw.Draw(text_bar_img)
    # 绘制深灰色背景
    bar_bg_color = (36, 36, 41, 230)
    text_bar_draw.rounded_rectangle(
        [20, 20, width - 40, 110], radius=8, fill=bar_bg_color
    )

    # 绘制顶部的金色高亮线
    accent_color = (203, 161, 95)
    text_bar_draw.rectangle([20, 20, width - 40, 26], fill=accent_color)

    # 左侧标题
    text_bar_draw.text((40, 60), "排行说明", GREY, waves_font_28, "lm")
    text_bar_draw.text(
        (185, 50),
        "1. 综合所有角色的声骸分数。具备声骸套装的角色，全量刷新面板后生效。",
        SPECIAL_GOLD,
        waves_font_20,
        "lm",
    )
    text_bar_draw.text(
        (185, 85), "2. 显示前10个最强角色", SPECIAL_GOLD, waves_font_20, "lm"
    )

    # 备注
    temp_notes = "排行标准：以所有角色声骸分数总和（角色分数>=175）为排序的综合排名"
    text_bar_draw.text((1260, 100), temp_notes, SPECIAL_GOLD, waves_font_16, "rm")

    card_img.alpha_composite(text_bar_img, (0, header_height))

    # 导入必要的图片资源
    bar = Image.open(TEXT_PATH / "bar1.png")

    # 获取头像
    details = rankInfoList.data.score_details
    tasks = [get_avatar(detail.user_id) for detail in details]
    results = await asyncio.gather(*tasks)

    # 获取角色信息
    bot_color_map = {}
    bot_color = copy.deepcopy(BOT_COLOR)

    # 绘制排行条目
    for rank_temp_index, temp in enumerate(zip(details, results)):
        detail, role_avatar = temp
        y_pos = header_height + 130 + rank_temp_index * item_spacing

        # 创建条目背景
        bar_bg = bar.copy()
        bar_bg.paste(role_avatar, (100, 0), role_avatar)
        bar_draw = ImageDraw.Draw(bar_bg)

        # 绘制排名
        rank_id = detail.rank
        rank_color = (54, 54, 54)
        if rank_id == 1:
            rank_color = (255, 0, 0)
        elif rank_id == 2:
            rank_color = (255, 180, 0)
        elif rank_id == 3:
            rank_color = (185, 106, 217)

        # 排名背景
        info_rank = Image.new("RGBA", (50, 50), color=(255, 255, 255, 0))
        rank_draw = ImageDraw.Draw(info_rank)
        rank_draw.rounded_rectangle(
            [0, 0, 50, 50], radius=8, fill=rank_color + (int(0.9 * 255),)
        )
        rank_draw.text((25, 25), f"{rank_id}", "white", waves_font_34, "mm")
        bar_bg.alpha_composite(info_rank, (40, 35))

        # 绘制玩家名字
        bar_draw.text((210, 75), f"{detail.kuro_name}", "white", waves_font_20, "lm")

        # 绘制角色数量
        char_count = len(detail.char_score_details) if detail.char_score_details else 0
        bar_draw.text((210, 45), "角色数:", (255, 255, 255), waves_font_18, "lm")
        bar_draw.text((280, 45), f"{char_count}", RED, waves_font_20, "lm")

        # uid
        uid_color = "white"
        if detail.waves_id == self_uid:
            uid_color = RED
        bar_draw.text(
            (350, 40), f"特征码: {detail.waves_id}", uid_color, waves_font_20, "lm"
        )

        # bot主人名字
        botName = getattr(detail, "alias_name", None)
        if botName:
            color = (54, 54, 54)
            if botName in bot_color_map:
                color = bot_color_map[botName]
            elif bot_color:
                color = bot_color.pop(0)
                bot_color_map[botName] = color

            info_block = Image.new("RGBA", (200, 30), color=(255, 255, 255, 0))
            info_block_draw = ImageDraw.Draw(info_block)
            info_block_draw.rounded_rectangle(
                [0, 0, 200, 30], radius=6, fill=color + (int(0.6 * 255),)
            )
            info_block_draw.text(
                (100, 15), f"bot: {botName}", "white", waves_font_18, "mm"
            )
            bar_bg.alpha_composite(info_block, (350, 66))

        # 总分数
        bar_draw.text(
            (1180, 45),
            f"{detail.total_score:.1f}",
            (255, 255, 255),
            waves_font_34,
            "mm",
        )
        bar_draw.text((1180, 75), "总分", "white", waves_font_16, "mm")

        # 绘制角色信息
        if detail.char_score_details:
            # 按分数排序，取前6名
            sorted_chars = sorted(
                detail.char_score_details, key=lambda x: x.phantom_score, reverse=True
            )[:10]

            # 在条目底部绘制前10名角色的头像
            char_size = 40
            char_spacing = 45
            char_start_x = 570
            char_start_y = 35

            for i, char in enumerate(sorted_chars):
                char_x = char_start_x + i * char_spacing

                # 获取角色头像
                char_avatar = await get_square_avatar(char.char_id)
                char_avatar = char_avatar.resize((char_size, char_size))

                # 应用圆形遮罩
                char_mask_img = Image.open(TEXT_PATH / "char_mask.png")
                char_mask_resized = char_mask_img.resize((char_size, char_size))
                char_avatar_masked = Image.new("RGBA", (char_size, char_size))
                char_avatar_masked.paste(char_avatar, (0, 0), char_mask_resized)

                # 粘贴头像
                bar_bg.paste(
                    char_avatar_masked, (char_x, char_start_y), char_avatar_masked
                )

                # 绘制分数
                score_text = f"{int(char.phantom_score)}"
                bar_draw.text(
                    (char_x + char_size // 2, char_start_y + char_size + 2),
                    score_text,
                    SPECIAL_GOLD,
                    waves_font_12,
                    "mm",
                )

            # 显示最高分
            if sorted_chars:
                best_score = f"{int(sorted_chars[0].phantom_score)} "
                bar_draw.text((1080, 45), best_score, "lightgreen", waves_font_30, "mm")
                bar_draw.text((1080, 75), "最高分", "white", waves_font_16, "mm")

        # 贴到背景
        card_img.paste(bar_bg, (0, y_pos), bar_bg)

    # title
    title_bg = Image.open(TEXT_PATH / "totalrank.jpg")
    title_bg = title_bg.crop((0, 0, width, 500))

    # icon
    icon = get_ICON()
    icon = icon.resize((128, 128))
    title_bg.paste(icon, (60, 240), icon)

    # title
    title_text = "#练度总排行"
    title_bg_draw = ImageDraw.Draw(title_bg)
    title_bg_draw.text((220, 290), title_text, "white", waves_font_58, "lm")

    # 遮罩
    char_mask = Image.open(TEXT_PATH / "char_mask.png").convert("RGBA")
    # 根据width扩图
    char_mask = char_mask.resize((width, char_mask.height * width // char_mask.width))
    char_mask = char_mask.crop((0, char_mask.height - 500, width, char_mask.height))
    char_mask_temp = Image.new("RGBA", char_mask.size, (0, 0, 0, 0))
    char_mask_temp.paste(title_bg, (0, 0), char_mask)

    card_img.paste(char_mask_temp, (0, 0), char_mask_temp)

    card_img = add_footer(card_img)
    return await convert_img(card_img)


async def get_avatar(
    qid: Optional[str],
) -> Image.Image:
    # 检查qid 为纯数字
    if qid and qid.isdigit():
        if WutheringWavesConfig.get_config("QQPicCache").data:
            pic = pic_cache.get(qid)
            if not pic:
                pic = await get_qq_avatar(qid, size=100)
                pic_cache.set(qid, pic)
        else:
            pic = await get_qq_avatar(qid, size=100)
            pic_cache.set(qid, pic)
        pic_temp = crop_center_img(pic, 120, 120)

        img = Image.new("RGBA", (180, 180))
        avatar_mask_temp = avatar_mask.copy()
        mask_pic_temp = avatar_mask_temp.resize((120, 120))
        img.paste(pic_temp, (0, -5), mask_pic_temp)
    else:
        default_avatar_char_id = "1505"
        pic = await get_square_avatar(default_avatar_char_id)

        pic_temp = Image.new("RGBA", pic.size)
        pic_temp.paste(pic.resize((160, 160)), (10, 10))
        pic_temp = pic_temp.resize((160, 160))

        avatar_mask_temp = avatar_mask.copy()
        mask_pic_temp = Image.new("RGBA", avatar_mask_temp.size)
        mask_pic_temp.paste(avatar_mask_temp, (-20, -45), avatar_mask_temp)
        mask_pic_temp = mask_pic_temp.resize((160, 160))

        img = Image.new("RGBA", (180, 180))
        img.paste(pic_temp, (0, 0), mask_pic_temp)

    return img
