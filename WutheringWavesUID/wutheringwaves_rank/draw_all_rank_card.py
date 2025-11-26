import asyncio
import copy
import time
from pathlib import Path
from typing import Optional, Union

import httpx
from PIL import Image, ImageDraw

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.api.wwapi import (
    GET_RANK_URL,
    RankDetail,
    RankInfoResponse,
    RankItem,
)
from ..utils.ascension.char import get_char_model
from ..utils.ascension.weapon import get_weapon_model
from ..utils.cache import TimedCache
from ..utils.database.models import WavesBind
from ..utils.fonts.waves_fonts import (
    waves_font_14,
    waves_font_16,
    waves_font_18,
    waves_font_20,
    waves_font_24,
    waves_font_28,
    waves_font_30,
    waves_font_34,
    waves_font_40,
    waves_font_44,
)
from ..utils.image import (
    AMBER,
    CHAIN_COLOR,
    GREY,
    RED,
    SPECIAL_GOLD,
    WAVES_FREEZING,
    WAVES_LINGERING,
    WAVES_MOLTEN,
    WAVES_MOONLIT,
    WAVES_SIERRA,
    WAVES_VOID,
    WEAPON_RESONLEVEL_COLOR,
    add_footer,
    crop_center_img,
    get_attribute,
    get_attribute_effect,
    get_qq_avatar,
    get_role_pile_old,
    get_square_avatar,
    get_square_weapon,
    get_waves_bg,
)
from ..utils.name_convert import alias_to_char_name, char_name_to_char_id
from ..utils.resource.constant import ATTRIBUTE_ID_MAP, SPECIAL_CHAR_NAME
from ..utils.util import get_version
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import WutheringWavesConfig

TEXT_PATH = Path(__file__).parent / "texture2d"
TITLE_I = Image.open(TEXT_PATH / "title.png")
TITLE_II = Image.open(TEXT_PATH / "title2.png")
avatar_mask = Image.open(TEXT_PATH / "avatar_mask.png")
weapon_icon_bg_3 = Image.open(TEXT_PATH / "weapon_icon_bg_3.png")
weapon_icon_bg_4 = Image.open(TEXT_PATH / "weapon_icon_bg_4.png")
weapon_icon_bg_5 = Image.open(TEXT_PATH / "weapon_icon_bg_5.png")
promote_icon = Image.open(TEXT_PATH / "promote_icon.png")
char_mask = Image.open(TEXT_PATH / "char_mask.png")
char_mask2 = Image.open(TEXT_PATH / "char_mask.png")
char_mask2 = char_mask2.resize((1300, char_mask2.size[1]))
logo_img = Image.open(TEXT_PATH / "logo_small_2.png")
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


async def get_rank(item: RankItem) -> Optional[RankInfoResponse]:
    WavesToken = WutheringWavesConfig.get_config("WavesToken").data

    if not WavesToken:
        return

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                GET_RANK_URL,
                json=item.dict(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {WavesToken}",
                },
                timeout=httpx.Timeout(10),
            )
            if res.status_code == 200:
                return RankInfoResponse.model_validate(res.json())
            else:
                logger.warning(f"获取排行失败: {res.status_code} - {res.text}")
        except Exception as e:
            logger.exception(f"获取排行失败: {e}")


async def draw_all_rank_card(
    bot: Bot, ev: Event, char: str, rank_type: str, pages: int
) -> Union[str, bytes]:
    is_self_ck = False
    self_uid = ""
    try:
        self_uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
        is_self_ck, ck = await waves_api.get_ck_result(self_uid, ev.user_id, ev.bot_id)
    except Exception:
        pass
    char_id = char_name_to_char_id(char)
    if not char_id:
        return (
            f"[鸣潮] 角色名【{char}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
        )
    char_name = alias_to_char_name(char)

    char_model = get_char_model(char_id)
    if not char_model:
        return (
            f"[鸣潮] 角色名【{char}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
        )

    attribute_name = ATTRIBUTE_ID_MAP[char_model.attributeId]

    start_time = time.time()
    logger.info(f"[get_rank_info_for_user] start: {start_time}")

    rank_type_num = 2 if rank_type == "伤害" else 1
    page_num = 20
    item = RankItem(
        char_id=int(char_id),
        page=pages,
        page_num=page_num,
        rank_type=rank_type_num,
        waves_id=self_uid,
        version=get_version(dynamic=True, waves_id=self_uid, char_id=char_id, rank_type=rank_type, pages=pages),
    )

    rankInfoList = await get_rank(item)
    if not rankInfoList:
        return "获取排行失败"

    if rankInfoList.message and not rankInfoList.data:
        return rankInfoList.message

    if not rankInfoList.data:
        return "获取排行失败"

    totalNum = len(rankInfoList.data.details)
    title_h = 500
    bar_star_h = 110
    text_bar_h = 130
    h = title_h + totalNum * bar_star_h + text_bar_h + 80
    card_img = get_waves_bg(1300, h, "bg3")
    # card_img_draw = ImageDraw.Draw(card_img)

    text_bar_img = Image.new("RGBA", (1300, text_bar_h), color=(0, 0, 0, 0))
    text_bar_draw = ImageDraw.Draw(text_bar_img)
    # 绘制深灰色背景
    bar_bg_color = (36, 36, 41, 230)
    text_bar_draw.rounded_rectangle(
        [20, 20, 1280, text_bar_h - 15], radius=8, fill=bar_bg_color
    )

    # 绘制顶部的金色高亮线
    accent_color = (203, 161, 95)
    text_bar_draw.rectangle([20, 20, 1280, 26], fill=accent_color)

    # 左侧标题
    text_bar_draw.text((40, 60), "上榜条件", GREY, waves_font_28, "lm")
    text_bar_draw.text((185, 50), "1. 声骸套装5件套", SPECIAL_GOLD, waves_font_20, "lm")
    text_bar_draw.text(
        (185, 85), "2. 登录用户&刷新面板", SPECIAL_GOLD, waves_font_20, "lm"
    )

    # 备注
    if rank_type == "伤害":
        temp_notes = (
            "排行标准：以期望伤害（计算暴击率的伤害，不代表实际伤害) 为排序的排名"
        )
    else:
        temp_notes = "排行标准：以声骸分数（声骸评分高，不代表实际伤害高) 为排序的排名"
    text_bar_draw.text((1260, 100), temp_notes, SPECIAL_GOLD, waves_font_16, "rm")

    card_img.alpha_composite(text_bar_img, (0, title_h))

    bar = Image.open(TEXT_PATH / "bar1.png")
    total_score = 0
    total_damage = 0

    pic = await get_square_avatar(char_id)

    pic_temp = Image.new("RGBA", pic.size)
    pic_temp.paste(pic.resize((160, 160)), (10, 10))
    pic_temp = pic_temp.resize((160, 160))

    tasks = [
        get_avatar(rank.user_id, rank.char_id) for rank in rankInfoList.data.details
    ]
    results = await asyncio.gather(*tasks)

    bot_color = copy.deepcopy(BOT_COLOR)
    bot_color_map = {}
    avg_num = 0
    for index, temp in enumerate(zip(rankInfoList.data.details, results)):
        rank: RankDetail = temp[0]
        role_avatar: Image.Image = temp[1]
        bar_bg = bar.copy()
        bar_star_draw = ImageDraw.Draw(bar_bg)
        bar_bg.paste(role_avatar, (100, 0), role_avatar)

        role_attribute = await get_attribute(attribute_name, is_simple=True)
        role_attribute = role_attribute.resize((40, 40)).convert("RGBA")
        bar_bg.alpha_composite(role_attribute, (300, 20))

        # 命座
        info_block = Image.new("RGBA", (46, 20), color=(255, 255, 255, 0))
        info_block_draw = ImageDraw.Draw(info_block)
        fill = CHAIN_COLOR[rank.chain] + (int(0.9 * 255),)
        info_block_draw.rounded_rectangle([0, 0, 46, 20], radius=6, fill=fill)
        info_block_draw.text(
            (5, 10), f"{get_chain_name(rank.chain)}", "white", waves_font_18, "lm"
        )
        bar_bg.alpha_composite(info_block, (190, 30))

        # 等级
        info_block = Image.new("RGBA", (60, 20), color=(255, 255, 255, 0))
        info_block_draw = ImageDraw.Draw(info_block)
        info_block_draw.rounded_rectangle(
            [0, 0, 60, 20], radius=6, fill=(54, 54, 54, int(0.9 * 255))
        )
        info_block_draw.text((5, 10), f"Lv.{rank.level}", "white", waves_font_18, "lm")
        bar_bg.alpha_composite(info_block, (240, 30))

        # 评分
        if rank.phantom_score > 0.0:
            score_bg = Image.open(TEXT_PATH / f"score_{rank.phantom_score_bg}.png")
            bar_bg.alpha_composite(score_bg, (545, 2))
            bar_star_draw.text(
                (707, 45),
                f"{int(rank.phantom_score * 100) / 100:.2f}",
                "white",
                waves_font_34,
                "mm",
            )
            bar_star_draw.text((707, 75), "声骸分数", SPECIAL_GOLD, waves_font_16, "mm")

        # 合鸣效果
        if rank.sonata_name:
            effect_image = await get_attribute_effect(rank.sonata_name)
            effect_image = effect_image.resize((50, 50))
            bar_bg.alpha_composite(effect_image, (790, 15))
            sonata_name = rank.sonata_name
        else:
            sonata_name = "合鸣效果"

        sonata_font = waves_font_16
        if len(sonata_name) > 4:
            sonata_font = waves_font_14
        bar_star_draw.text((815, 75), f"{sonata_name}", "white", sonata_font, "mm")

        # 武器
        weapon_bg_temp = Image.new("RGBA", (600, 300))

        weapon_model = get_weapon_model(rank.weapon_id)
        if not weapon_model:
            logger.warning(
                f"武器名【{rank.weapon_id}】无法找到, 可能暂未适配, 请先检查输入是否正确！"
            )
            continue

        weapon_icon = await get_square_weapon(rank.weapon_id)
        weapon_icon = crop_center_img(weapon_icon, 110, 110)
        weapon_icon_bg = get_weapon_icon_bg(weapon_model.starLevel)
        weapon_icon_bg.paste(weapon_icon, (10, 20), weapon_icon)

        weapon_bg_temp_draw = ImageDraw.Draw(weapon_bg_temp)
        weapon_bg_temp_draw.text(
            (200, 30),
            f"{weapon_model.name}",
            SPECIAL_GOLD,
            waves_font_40,
            "lm",
        )
        weapon_bg_temp_draw.text(
            (203, 75), f"Lv.{rank.level}/90", "white", waves_font_30, "lm"
        )

        _x = 220
        _y = 120
        wrc_fill = WEAPON_RESONLEVEL_COLOR[rank.weapon_reson_level] + (int(0.8 * 255),)
        weapon_bg_temp_draw.rounded_rectangle(
            [_x - 15, _y - 15, _x + 50, _y + 15], radius=7, fill=wrc_fill
        )
        weapon_bg_temp_draw.text(
            (_x, _y), f"精{rank.weapon_reson_level}", "white", waves_font_24, "lm"
        )

        weapon_bg_temp.alpha_composite(weapon_icon_bg, dest=(45, 0))

        bar_bg.alpha_composite(weapon_bg_temp.resize((260, 130)), dest=(850, 25))

        # 伤害
        bar_star_draw.text(
            (1140, 45),
            f"{rank.expected_damage:,.0f}",
            SPECIAL_GOLD,
            waves_font_34,
            "mm",
        )
        bar_star_draw.text(
            (1140, 75), f"{rank.expected_name}", "white", waves_font_16, "mm"
        )

        # 排名
        rank_id = rank.rank
        rank_color = (54, 54, 54)
        if rank_id == 1:
            rank_color = (255, 0, 0)
        elif rank_id == 2:
            rank_color = (255, 180, 0)
        elif rank_id == 3:
            rank_color = (185, 106, 217)

        def draw_rank_id(rank_id, size=(50, 50), draw=(24, 24), dest=(40, 30)):
            info_rank = Image.new("RGBA", size, color=(255, 255, 255, 0))
            rank_draw = ImageDraw.Draw(info_rank)
            rank_draw.rounded_rectangle(
                [0, 0, size[0], size[1]], radius=8, fill=rank_color + (int(0.9 * 255),)
            )
            rank_draw.text(draw, f"{rank_id}", "white", waves_font_34, "mm")
            bar_bg.alpha_composite(info_rank, dest)

        # rank_id = index + 1 + (pages - 1) * 20
        if rank_id > 999:
            draw_rank_id("999+", size=(100, 50), draw=(50, 24), dest=(10, 30))
        elif rank_id > 99:
            draw_rank_id(rank_id, size=(75, 50), draw=(37, 24), dest=(25, 30))
        else:
            draw_rank_id(rank_id, size=(50, 50), draw=(24, 24), dest=(40, 30))

        # 名字
        bar_star_draw.text((210, 75), f"{rank.kuro_name}", "white", waves_font_20, "lm")

        # uid
        uid_color = "white"
        if is_self_ck and self_uid == rank.waves_id:
            uid_color = RED
        bar_star_draw.text(
            (350, 40), f"特征码: {rank.waves_id}", uid_color, waves_font_20, "lm"
        )

        # bot主人名字
        botName = rank.alias_name if rank.alias_name else ""
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
            bar_bg.alpha_composite(info_block, (350, 65))

        # 贴到背景
        card_img.paste(bar_bg, (0, title_h + text_bar_h + index * bar_star_h), bar_bg)

        if index + 1 + (pages - 1) * page_num == rank_id:
            total_score += rank.phantom_score
            total_damage += rank.expected_damage
            avg_num += 1

    avg_score = f"{total_score / avg_num:.1f}" if avg_num != 0 else "0"
    avg_damage = f"{total_damage / avg_num:,.0f}" if avg_num != 0 else "0"

    title = TITLE_II.copy()
    title_draw = ImageDraw.Draw(title)
    # logo
    title.alpha_composite(logo_img.copy(), dest=(350, 65))

    title_draw.text((600, 335), f"{avg_score}", "white", waves_font_44, "mm")
    title_draw.text((600, 375), "平均声骸分数", SPECIAL_GOLD, waves_font_20, "mm")

    title_draw.text((790, 335), f"{avg_damage}", "white", waves_font_44, "mm")
    title_draw.text((790, 375), "平均伤害", SPECIAL_GOLD, waves_font_20, "mm")

    if char_id in SPECIAL_CHAR_NAME:
        char_name = SPECIAL_CHAR_NAME[char_id]

    title_name = f"{char_name}{rank_type}总排行"
    title_draw.text((540, 265), f"{title_name}", "black", waves_font_30, "lm")

    # 时间
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    title_draw.text((470, 205), f"{time_str}", GREY, waves_font_20, "lm")

    # 版本
    info_block = Image.new("RGBA", (100, 30), color=(255, 255, 255, 0))
    info_block_draw = ImageDraw.Draw(info_block)
    info_block_draw.rounded_rectangle(
        [0, 0, 100, 30], radius=6, fill=(0, 79, 152, int(0.9 * 255))
    )
    info_block_draw.text((50, 15), f"v{get_version()}", "white", waves_font_24, "mm")
    _x = 540 + 31 * len(title_name)
    title.alpha_composite(info_block, (_x, 255))

    img_temp = Image.new("RGBA", char_mask2.size)
    img_temp.alpha_composite(title, (-300, 0))
    # 人物bg
    pile = await get_role_pile_old(char_id, custom=True)
    img_temp.alpha_composite(pile, (600, -120))

    img_temp2 = Image.new("RGBA", char_mask2.size)
    img_temp2.paste(img_temp, (0, 0), char_mask2.copy())

    card_img.alpha_composite(img_temp2, (0, 0))
    card_img = add_footer(card_img)
    card_img = await convert_img(card_img)

    logger.info(f"[get_rank_info_for_user] end: {time.time() - start_time}")
    return card_img


def get_chain_name(n: int) -> str:
    return f"{['零', '一', '二', '三', '四', '五', '六'][n]}链"


def get_weapon_icon_bg(star: int = 3) -> Image.Image:
    if star < 3:
        star = 3
    bg_path = TEXT_PATH / f"weapon_icon_bg_{star}.png"
    bg_img = Image.open(bg_path)
    return bg_img


def get_breach(breach: Union[int, None], level: int):
    if breach is None:
        if level <= 20:
            breach = 0
        elif level <= 40:
            breach = 1
        elif level <= 50:
            breach = 2
        elif level <= 60:
            breach = 3
        elif level <= 70:
            breach = 4
        elif level <= 80:
            breach = 5
        elif level <= 90:
            breach = 6
        else:
            breach = 0

    return breach


async def get_avatar(
    qid: Optional[str],
    char_id: Union[int, str],
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
        pic = await get_square_avatar(char_id)

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
