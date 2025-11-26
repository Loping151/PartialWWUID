import asyncio
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

from PIL import Image, ImageDraw

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.api.model import AccountBaseInfo, DailyData
from ..utils.api.request_util import KuroApiResp
from ..utils.database.models import WavesBind, WavesUser
from ..utils.error_reply import ERROR_CODE, WAVES_CODE_102, WAVES_CODE_103
from ..utils.fonts.waves_fonts import (
    waves_font_24,
    waves_font_25,
    waves_font_26,
    waves_font_30,
    waves_font_32,
    waves_font_42,
)
from ..utils.image import (
    GOLD,
    GREEN,
    GREY,
    RED,
    YELLOW,
    add_footer,
    get_event_avatar,
    get_random_waves_role_pile,
)
from ..utils.name_convert import char_name_to_char_id
from ..utils.resource.constant import SPECIAL_CHAR
from ..utils.waves_api import waves_api

TEXT_PATH = Path(__file__).parent / "texture2d"
YES = Image.open(TEXT_PATH / "yes.png")
YES = YES.resize((40, 40))
NO = Image.open(TEXT_PATH / "no.png")
NO = NO.resize((40, 40))
bar_down = Image.open(TEXT_PATH / "bar_down.png")

based_w = 1150
based_h = 850


async def seconds2hours(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return "%02d小时%02d分" % (h, m)


async def process_uid(uid, ev):
    ck = await waves_api.get_self_waves_ck(uid, ev.user_id, ev.bot_id)
    if not ck:
        return None

    # 并行请求所有相关 API
    results = await asyncio.gather(
        waves_api.get_daily_info(uid, ck),
        waves_api.get_base_info(uid, ck),
        return_exceptions=True,
    )

    (daily_info_res, account_info_res) = results
    if not isinstance(daily_info_res, KuroApiResp) or not daily_info_res.success:
        return None

    if not isinstance(account_info_res, KuroApiResp) or not account_info_res.success:
        return None

    daily_info = DailyData.model_validate(daily_info_res.data)
    account_info = AccountBaseInfo.model_validate(account_info_res.data)

    return {
        "daily_info": daily_info,
        "account_info": account_info,
    }


async def draw_stamina_img(bot: Bot, ev: Event):
    try:
        uid_list = await WavesBind.get_uid_list_by_game(ev.user_id, ev.bot_id)
        logger.info(f"[鸣潮][每日信息]UID: {uid_list}")
        if uid_list is None:
            return ERROR_CODE[WAVES_CODE_103]
        # 进行校验UID是否绑定CK
        tasks = [process_uid(uid, ev) for uid in uid_list]
        results = await asyncio.gather(*tasks)

        # 过滤掉 None 值
        valid_daily_list = [res for res in results if res is not None]

        if len(valid_daily_list) == 0:
            return ERROR_CODE[WAVES_CODE_102]

        # 开始绘图任务
        task = []
        img = Image.new(
            "RGBA", (based_w, based_h * len(valid_daily_list)), (0, 0, 0, 0)
        )
        for uid_index, valid in enumerate(valid_daily_list):
            task.append(_draw_all_stamina_img(ev, img, valid, uid_index))
        await asyncio.gather(*task)
        res = await convert_img(img)
        logger.info("[鸣潮][每日信息]绘图已完成,等待发送!")
    except TypeError:
        logger.exception("[鸣潮][每日信息]绘图失败!")
        res = "你绑定过的UID中可能存在过期CK~请重新绑定一下噢~"

    return res


async def _draw_all_stamina_img(ev: Event, img: Image.Image, valid: Dict, index: int):
    stamina_img = await _draw_stamina_img(ev, valid)
    stamina_img = stamina_img.convert("RGBA")
    img.paste(stamina_img, (0, based_h * index), stamina_img)


async def _draw_stamina_img(ev: Event, valid: Dict) -> Image.Image:
    daily_info: DailyData = valid["daily_info"]
    account_info: AccountBaseInfo = valid["account_info"]
    if daily_info.hasSignIn:
        sign_in_icon = YES
        sing_in_text = "签到已完成！"
    else:
        sign_in_icon = NO
        sing_in_text = "今日未签到！"

    if (
        daily_info.livenessData.total != 0
        and daily_info.livenessData.cur == daily_info.livenessData.total
    ):
        active_icon = YES
        active_text = "活跃度已满！"
    else:
        active_icon = NO
        active_text = "活跃度未满！"

    img = Image.open(TEXT_PATH / "bg.jpg").convert("RGBA")
    info = Image.open(TEXT_PATH / "main_bar.png").convert("RGBA")
    base_info_bg = Image.open(TEXT_PATH / "base_info_bg.png")
    avatar_ring = Image.open(TEXT_PATH / "avatar_ring.png")

    # 头像
    avatar = await draw_pic_with_ring(ev)

    # 随机获得pile
    user = await WavesUser.get_user_by_attr(
        ev.user_id, ev.bot_id, "uid", daily_info.roleId
    )
    pile_id = None
    if user and user.stamina_bg_value:
        char_id = char_name_to_char_id(user.stamina_bg_value)
        if char_id in SPECIAL_CHAR:
            ck = await waves_api.get_self_waves_ck(
                daily_info.roleId, ev.user_id, ev.bot_id
            )
            if ck:
                for char_id in SPECIAL_CHAR[char_id]:
                    role_detail_info = await waves_api.get_role_detail_info(
                        char_id, daily_info.roleId, ck
                    )
                    if not role_detail_info.success:
                        continue
                    role_detail_info = role_detail_info.data
                    if (
                        not isinstance(role_detail_info, Dict)
                        or "role" not in role_detail_info
                        or role_detail_info["role"] is None
                        or "level" not in role_detail_info
                        or role_detail_info["level"] is None
                    ):
                        continue
                    pile_id = char_id
                    break
        else:
            pile_id = char_id
    pile = await get_random_waves_role_pile(pile_id)
    # pile = pile.crop((0, 0, pile.size[0], pile.size[1] - 155))

    base_info_draw = ImageDraw.Draw(base_info_bg)
    base_info_draw.text(
        (275, 120), f"{daily_info.roleName[:7]}", GREY, waves_font_30, "lm"
    )
    base_info_draw.text(
        (226, 173), f"特征码:  {daily_info.roleId}", GOLD, waves_font_25, "lm"
    )
    # 账号基本信息，由于可能会没有，放在一起

    title_bar = Image.open(TEXT_PATH / "title_bar.png")
    title_bar_draw = ImageDraw.Draw(title_bar)
    title_bar_draw.text((480, 125), "战歌重奏", GREY, waves_font_26, "mm")
    color = RED if account_info.weeklyInstCount != 0 else GREEN
    if (
        account_info.weeklyInstCountLimit is not None
        and account_info.weeklyInstCount is not None
    ):
        title_bar_draw.text(
            (480, 78),
            f"{account_info.weeklyInstCountLimit - account_info.weeklyInstCount} / {account_info.weeklyInstCountLimit}",
            color,
            waves_font_42,
            "mm",
        )

    title_bar_draw.text((630, 125), "先约电台", GREY, waves_font_26, "mm")
    title_bar_draw.text(
        (630, 78),
        f"Lv.{daily_info.battlePassData[0].cur}",
        "white",
        waves_font_42,
        "mm",
    )

    # logo_img = get_small_logo(2)
    # title_bar.alpha_composite(logo_img, dest=(760, 60))

    color = RED if account_info.rougeScore != account_info.rougeScoreLimit else GREEN
    title_bar_draw.text((810, 125), "千道门扉的异想", GREY, waves_font_26, "mm")
    title_bar_draw.text(
        (810, 78),
        f"{account_info.rougeScore}/{account_info.rougeScoreLimit}",
        color,
        waves_font_32,
        "mm",
    )

    # 体力剩余恢复时间
    active_draw = ImageDraw.Draw(info)
    curr_time = int(time.time())
    refreshTimeStamp = (
        daily_info.energyData.refreshTimeStamp
        if daily_info.energyData.refreshTimeStamp
        else curr_time
    )
    # remain_time = await seconds2hours(refreshTimeStamp - curr_time)

    time_img = Image.new("RGBA", (190, 33), (255, 255, 255, 0))
    time_img_draw = ImageDraw.Draw(time_img)
    time_img_draw.rounded_rectangle(
        [0, 0, 190, 33], radius=15, fill=(186, 55, 42, int(0.7 * 255))
    )
    if refreshTimeStamp != curr_time:
        date_from_timestamp = datetime.fromtimestamp(refreshTimeStamp)
        now = datetime.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)

        remain_time = datetime.fromtimestamp(refreshTimeStamp).strftime(
            "%m.%d %H:%M:%S"
        )
        if date_from_timestamp.date() == today:
            remain_time = "今天 " + datetime.fromtimestamp(refreshTimeStamp).strftime(
                "%H:%M:%S"
            )
        elif date_from_timestamp.date() == tomorrow:
            remain_time = "明天 " + datetime.fromtimestamp(refreshTimeStamp).strftime(
                "%H:%M:%S"
            )

        time_img_draw.text((10, 15), f"{remain_time}", "white", waves_font_24, "lm")
    else:
        time_img_draw.text((10, 15), "漂泊者该上潮了", "white", waves_font_24, "lm")

    info.alpha_composite(time_img, (280, 50))

    max_len = 345
    # 体力
    active_draw.text(
        (350, 115), f"/{daily_info.energyData.total}", GREY, waves_font_30, "lm"
    )
    active_draw.text(
        (348, 115), f"{daily_info.energyData.cur}", GREY, waves_font_30, "rm"
    )
    radio = daily_info.energyData.cur / daily_info.energyData.total
    color = RED if radio > 0.8 else YELLOW
    active_draw.rectangle((173, 142, int(173 + radio * max_len), 150), color)

    # 结晶单质
    active_draw.text(
        (350, 230), f"/{account_info.storeEnergyLimit}", GREY, waves_font_30, "lm"
    )
    active_draw.text(
        (348, 230), f"{account_info.storeEnergy}", GREY, waves_font_30, "rm"
    )
    radio = (
        account_info.storeEnergy / account_info.storeEnergyLimit
        if account_info.storeEnergyLimit is not None
        and account_info.storeEnergy is not None
        and account_info.storeEnergyLimit != 0
        else 0
    )
    color = RED if radio > 0.8 else YELLOW
    active_draw.rectangle((173, 254, int(173 + radio * max_len), 262), color)

    # 活跃度
    active_draw.text(
        (350, 350), f"/{daily_info.livenessData.total}", GREY, waves_font_30, "lm"
    )
    active_draw.text(
        (348, 350), f"{daily_info.livenessData.cur}", GREY, waves_font_30, "rm"
    )
    radio = (
        daily_info.livenessData.cur / daily_info.livenessData.total
        if daily_info.livenessData.total != 0
        else 0
    )
    active_draw.rectangle((173, 374, int(173 + radio * max_len), 382), YELLOW)

    # 签到状态
    status_img = Image.new("RGBA", (230, 40), (255, 255, 255, 0))
    status_img_draw = ImageDraw.Draw(status_img)
    status_img_draw.rounded_rectangle([0, 0, 230, 40], fill=(0, 0, 0, int(0.3 * 255)))
    status_img.alpha_composite(sign_in_icon, (0, 0))
    status_img_draw.text((50, 20), f"{sing_in_text}", "white", waves_font_30, "lm")
    img.alpha_composite(status_img, (70, 80))

    # 活跃状态
    status_img2 = Image.new("RGBA", (230, 40), (255, 255, 255, 0))
    status_img2_draw = ImageDraw.Draw(status_img2)
    status_img2_draw.rounded_rectangle([0, 0, 230, 40], fill=(0, 0, 0, int(0.3 * 255)))
    status_img2.alpha_composite(active_icon, (0, 0))
    status_img2_draw.text((50, 20), f"{active_text}", "white", waves_font_30, "lm")
    img.alpha_composite(status_img2, (70, 140))

    # bbs状态
    # status_img3 = Image.new("RGBA", (300, 40), (255, 255, 255, 0))
    # status_img3_draw = ImageDraw.Draw(status_img3)
    # status_img3_draw.rounded_rectangle([0, 0, 300, 40], fill=(0, 0, 0, int(0.3 * 255)))
    # status_img3.alpha_composite(bbs_icon, (0, 0))
    # status_img3_draw.text((50, 20), f"{bbs_text}", "white", waves_font_30, "lm")
    # img.alpha_composite(status_img3, (70, 80))

    # pile 放在背景上
    img.paste(pile, (550, -150), pile)
    # 贴个bar_down
    img.alpha_composite(bar_down, (0, 0))
    # info 放在背景上
    img.paste(info, (0, 190), info)
    # base_info 放在背景上
    img.paste(base_info_bg, (40, 570), base_info_bg)
    # avatar_ring 放在背景上
    img.paste(avatar_ring, (40, 620), avatar_ring)
    img.paste(avatar, (40, 620), avatar)
    # account_info 放背景上
    img.paste(title_bar, (190, 620), title_bar)
    img = add_footer(img, 600, 25)
    return img


async def draw_pic_with_ring(ev: Event):
    pic = await get_event_avatar(ev, is_valid_at_param=False)

    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    img = Image.new("RGBA", (200, 200))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    img.paste(resize_pic, (20, 20), mask)

    return img
