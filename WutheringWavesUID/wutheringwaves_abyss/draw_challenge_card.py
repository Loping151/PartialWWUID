from datetime import timedelta
from pathlib import Path
from typing import Union

from PIL import Image, ImageDraw

from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img

from ..utils.api.model import AccountBaseInfo, ChallengeArea, RoleList
from ..utils.error_reply import WAVES_CODE_102
from ..utils.fonts.waves_fonts import (
    waves_font_18,
    waves_font_20,
    waves_font_24,
    waves_font_25,
    waves_font_26,
    waves_font_30,
    waves_font_42,
)
from ..utils.hint import error_reply
from ..utils.image import (
    GOLD,
    GREY,
    SPECIAL_GOLD,
    add_footer,
    get_waves_bg,
    pic_download_from_url,
)
from ..utils.imagetool import draw_pic, draw_pic_with_ring
from ..utils.name_convert import char_name_to_char_id
from ..utils.resource.RESOURCE_PATH import CHALLENGE_PATH
from ..utils.waves_api import waves_api

TEXT_PATH = Path(__file__).parent / "texture2d"

ERROR_MSG = "获取全息数据失败，请稍后再试"
ERROR_UNLOCK = "您未解锁[全息挑战]"
ERROR_OPEN = "您未打开库街区[全息挑战]的对外展示"
ERROR_NO_CHALLENGE = "您未通关任何全息战略"


async def draw_challenge_img(ev: Event, uid: str, user_id: str) -> Union[bytes, str]:
    is_self_ck, ck = await waves_api.get_ck_result(uid, user_id, ev.bot_id)
    if not ck:
        return error_reply(WAVES_CODE_102)

    # 全息数据
    challenge_data = await waves_api.get_challenge_data(uid, ck)
    if not challenge_data.success:
        return challenge_data.throw_msg()

    challenge_data = ChallengeArea.model_validate(challenge_data.data)
    if not challenge_data.isUnlock:
        return ERROR_UNLOCK

    if not challenge_data.open:
        return ERROR_OPEN

    # 账户数据
    account_info = await waves_api.get_base_info(uid, ck)
    if not account_info.success:
        return account_info.throw_msg()
    account_info = AccountBaseInfo.model_validate(account_info.data)

    # 共鸣者信息
    role_info = await waves_api.get_role_info(uid, ck)
    if not role_info.success:
        return role_info.throw_msg()

    role_info = RoleList.model_validate(role_info.data)

    num = len(challenge_data.challengeInfo)
    a = num // 2 + (0 if num % 2 == 0 else 1)
    h = 300 + a * 260 + 50
    card_img = get_waves_bg(1560, h, "bg8")

    # 基础信息 名字 特征码
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

    challenge_index = 0
    for _challenge in reversed(challenge_data.challengeInfo.values()):
        img_temp = Image.new("RGBA", (750, 250), color=(0, 0, 0, 0))
        img_temp_draw = ImageDraw.Draw(img_temp)

        # 蓝色到黑色的渐变
        # gradient_rect = create_gradient_rectangle_pillow(
        #     (730, 230),
        #     color1=(30, 50, 90, 140),  # 深蓝色，半透明
        #     color2=(0, 0, 10, 80),  # 接近黑色，更透明
        #     direction="vertical",
        #     radius=10,
        # )
        # img_temp.paste(gradient_rect, (10, 10), gradient_rect)
        img_temp_draw.rounded_rectangle(
            (10, 10, 740, 240),
            10,
            fill=(0, 0, 0, 80),
            outline=(30, 50, 90, 120),
            width=5,
        )

        max_num = len(_challenge)

        boss_difficulty = 1
        boss_level = 1
        boss_icon = await pic_download_from_url(
            CHALLENGE_PATH, _challenge[0].bossIconUrl
        )
        boss_icon = boss_icon.resize((242, 156))
        img_temp.alpha_composite(boss_icon, (20, 20))
        for _temp in reversed(_challenge):
            boss_difficulty = _temp.difficulty
            boss_level = _temp.bossLevel
            if not _temp.roles:
                continue
            img_temp_draw.text(
                (450, 30),
                f"通关时间：{timedelta(seconds=_temp.passTime)}",
                "white",
                waves_font_24,
                "lm",
            )

            for role_index, _role in enumerate(_temp.roles):
                role = next(
                    (
                        role
                        for role in role_info.roleList
                        if role.roleName == _role.roleName
                        or _role.roleName in role.roleName
                    ),
                    None,
                )
                if not role:
                    roleId = char_name_to_char_id(_role.roleName)
                    avatar = await draw_pic(roleId)
                    char_bg = Image.open(TEXT_PATH / f"char_bg{5}.png")
                else:
                    avatar = await draw_pic(role.roleId)
                    char_bg = Image.open(TEXT_PATH / f"char_bg{role.starLevel}.png")

                char_bg_draw = ImageDraw.Draw(char_bg)
                char_bg_draw.text(
                    (90, 150), f"{_role.roleName}", "white", waves_font_18, "mm"
                )
                char_bg.paste(avatar, (0, 0), avatar)

                info_block = Image.new("RGBA", (40, 20), color=(255, 255, 255, 0))
                info_block_draw = ImageDraw.Draw(info_block)
                info_block_draw.rectangle(
                    [0, 0, 40, 20], fill=(96, 12, 120, int(0.9 * 255))
                )
                info_block_draw.text(
                    (2, 10), f"{_role.roleLevel}", "white", waves_font_18, "lm"
                )
                char_bg.paste(info_block, (110, 35), info_block)

                img_temp.alpha_composite(char_bg, (260 + role_index * 150, 80))

            break

        img_temp_draw.text(
            (30, 210),
            f"{_challenge[0].bossName}",
            SPECIAL_GOLD,
            waves_font_30,
            "lm",
        )
        # _challenge[0].bossName 计算字体宽度
        boss_name_length = len(_challenge[0].bossName)
        length_width = boss_name_length * 33
        img_temp_draw.text(
            (30 + length_width, 210), f"Lv.{boss_level}", "white", waves_font_20, "lm"
        )
        img_temp_draw.text(
            (450, 70),
            f"当前难度：{boss_difficulty}/{max_num}",
            GOLD,
            waves_font_24,
            "lm",
        )

        card_img.alpha_composite(
            img_temp,
            (25 + challenge_index % 2 * 760, 300 + challenge_index // 2 * 260),
        )
        challenge_index += 1

    card_img = add_footer(card_img, 600, 20)
    card_img = await convert_img(card_img)
    return card_img
