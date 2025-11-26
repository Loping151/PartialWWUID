import copy
import re
from pathlib import Path
from typing import Dict, Optional

import httpx
from PIL import Image, ImageDraw, ImageEnhance

from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img, get_qq_avatar

from ..utils import hint
from ..utils.api.model import (
    AccountBaseInfo,
    OnlineRoleList,
    RoleDetailData,
    WeaponData,
)
from ..utils.api.model_other import EnemyDetailData
from ..utils.api.wwapi import ONE_RANK_URL, OneRankRequest, OneRankResponse
from ..utils.ascension.char import get_char_model
from ..utils.ascension.template import get_template_data
from ..utils.ascension.weapon import (
    WavesWeaponResult,
    get_breach,
    get_weapon_detail,
    get_weapon_model,
)
from ..utils.calc import WuWaCalc
from ..utils.calculate import (
    calc_phantom_entry,
    calc_phantom_score,
    get_calc_map,
    get_max_score,
    get_total_score_bg,
    get_valid_color,
)
from ..utils.char_info_utils import get_all_roleid_detail_info
from ..utils.damage.abstract import DamageDetailRegister
from ..utils.error_reply import WAVES_CODE_102
from ..utils.fonts.waves_fonts import (
    waves_font_16,
    waves_font_18,
    waves_font_20,
    waves_font_24,
    waves_font_25,
    waves_font_26,
    waves_font_28,
    waves_font_30,
    waves_font_36,
    waves_font_40,
    waves_font_42,
    waves_font_50,
)
from ..utils.image import (
    GOLD,
    GREY,
    SPECIAL_GOLD,
    WAVES_FREEZING,
    WAVES_MOONLIT,
    WAVES_SHUXING_MAP,
    WEAPON_RESONLEVEL_COLOR,
    add_footer,
    change_color,
    draw_text_with_shadow,
    get_attribute,
    get_attribute_effect,
    get_attribute_prop,
    get_custom_gaussian_blur,
    get_event_avatar,
    get_role_pile,
    get_small_logo,
    get_square_avatar,
    get_square_weapon,
    get_waves_bg,
    get_weapon_type,
)
from ..utils.name_convert import alias_to_char_name, char_name_to_char_id
from ..utils.resource.constant import (
    ATTRIBUTE_ID_MAP,
    DEAFAULT_WEAPON_ID,
    SPECIAL_CHAR,
    WEAPON_TYPE_ID_MAP,
    get_short_name,
)
from ..utils.resource.download_file import (
    get_chain_img,
    get_phantom_img,
    get_skill_img,
)
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import PREFIX
from ..wutheringwaves_config.wutheringwaves_config import (
    ShowConfig,
    WutheringWavesConfig,
)
from .role_info_change import change_role_detail

TEXT_PATH = Path(__file__).parent / "texture2d"

ph_sort_name = [
    [("生命", "0"), ("攻击", "0"), ("防御", "0"), ("共鸣效率", "0%")],
    [
        ("暴击", "0.0%"),
        ("暴击伤害", "0.0%"),
        ("属性伤害加成", "0.0%"),
        ("治疗效果加成", "0.0%"),
    ],
    [
        ("普攻伤害加成", "0.0%"),
        ("重击伤害加成", "0.0%"),
        ("共鸣技能伤害加成", "0.0%"),
        ("共鸣解放伤害加成", "0.0%"),
    ],
]

card_sort_map = {
    "生命": "0",
    "攻击": "0",
    "防御": "0",
    "共鸣效率": "0%",
    "暴击": "0.0%",
    "暴击伤害": "0.0%",
    "属性伤害加成": "0.0%",
    "治疗效果加成": "0.0%",
    "普攻伤害加成": "0.0%",
    "重击伤害加成": "0.0%",
    "共鸣技能伤害加成": "0.0%",
    "共鸣解放伤害加成": "0.0%",
}

card_sort_name = [
    ("生命", "0"),
    ("攻击", "0"),
    ("防御", "0"),
    ("共鸣效率", "0%"),
    ("暴击", "0.0%"),
    ("暴击伤害", "0.0%"),
    ("属性伤害加成", "0.0%"),
    ("治疗效果加成", "0.0%"),
]

weight_list = [
    "属性,C4主词条权重,C3主词条权重,C1主词条权重,副词条权重",
    "生命",
    "生命%",
    "攻击",
    "攻击%",
    "防御",
    "防御%",
    "共鸣效率",
    "暴击",
    "暴击伤害",
    "属性伤害加成",
    "治疗效果加成",
    "普攻伤害加成",
    "重击伤害加成",
    "共鸣技能伤害加成",
    "共鸣解放伤害加成",
]

damage_bar1 = Image.open(TEXT_PATH / "damage_bar1.png")
damage_bar2 = Image.open(TEXT_PATH / "damage_bar2.png")


async def get_one_rank(item: OneRankRequest) -> Optional[OneRankResponse]:
    WavesToken = WutheringWavesConfig.get_config("WavesToken").data

    if not WavesToken:
        return

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(
                ONE_RANK_URL,
                json=item.dict(),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {WavesToken}",
                },
                timeout=httpx.Timeout(10),
            )
            # logger.debug(f"获取排行: {res.text}")
            if res.status_code == 200:
                return OneRankResponse.model_validate(res.json())
        except Exception as e:
            logger.exception(f"获取排行失败: {e}")


def parse_text_and_number(text):
    match = re.match(r"([^\d]+)(\d*)", text)

    if match:
        text_part = match.group(1)  # 获取文字部分
        number_part = match.group(2)  # 获取数字部分，如果有的话
        return text_part, number_part if number_part else None
    else:
        return text, None


async def ph_card_draw(
    ph_sum_value,
    role_detail: RoleDetailData,
    is_draw=True,
    change_command="",
    enemy_detail: Optional[EnemyDetailData] = None,
):
    char_name = role_detail.role.roleName

    phantom_temp = Image.new("RGBA", (1200, 1280 + ph_sum_value))
    banner3 = Image.open(TEXT_PATH / "banner3.png")
    phantom_temp.alpha_composite(banner3, dest=(0, 0))

    ph_0 = Image.open(TEXT_PATH / "ph_0.png")
    ph_1 = Image.open(TEXT_PATH / "ph_1.png")
    #  phantom_sum_value = {}
    calc = WuWaCalc(role_detail, enemy_detail)
    if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
        equipPhantomList = role_detail.phantomData.equipPhantomList
        phantom_score = 0

        calc.phantom_pre = calc.prepare_phantom()
        calc.phantom_card = calc.enhance_summation_phantom_value(calc.phantom_pre)
        calc.calc_temp = get_calc_map(
            calc.phantom_card,
            role_detail.role.roleName,
            role_detail.role.roleId,
        )

        for i, _phantom in enumerate(equipPhantomList):
            sh_temp = Image.new("RGBA", (350, 550))
            sh_temp_draw = ImageDraw.Draw(sh_temp)
            sh_bg = Image.open(TEXT_PATH / "sh_bg.png")
            sh_temp.alpha_composite(sh_bg, dest=(0, 0))
            if _phantom and _phantom.phantomProp:
                props = _phantom.get_props()
                _score, _bg = calc_phantom_score(
                    role_detail.role.roleId, props, _phantom.cost, calc.calc_temp
                )

                phantom_score += _score
                sh_title = Image.open(TEXT_PATH / f"sh_title_{_bg}.png")

                sh_temp.alpha_composite(sh_title, dest=(0, 0))

                phantom_icon = await get_phantom_img(
                    _phantom.phantomProp.phantomId, _phantom.phantomProp.iconUrl
                )
                fetter_icon = await get_attribute_effect(_phantom.fetterDetail.name)
                fetter_icon = fetter_icon.resize((50, 50))
                phantom_icon.alpha_composite(fetter_icon, dest=(205, 0))
                phantom_icon = phantom_icon.resize((100, 100))
                sh_temp.alpha_composite(phantom_icon, dest=(20, 20))
                phantomName = (
                    _phantom.phantomProp.name.replace("·", " ")
                    .replace("（", " ")
                    .replace("）", "")
                )
                short_name = get_short_name(_phantom.phantomProp.phantomId, phantomName)
                sh_temp_draw.text(
                    (130, 40), f"{short_name}", SPECIAL_GOLD, waves_font_28, "lm"
                )

                # 声骸等级背景
                ph_level_img = Image.new("RGBA", (84, 30), (255, 255, 255, 0))
                ph_level_img_draw = ImageDraw.Draw(ph_level_img)
                ph_level_img_draw.rounded_rectangle(
                    [0, 0, 84, 30], radius=8, fill=(0, 0, 0, int(0.8 * 255))
                )
                ph_level_img_draw.text(
                    (8, 13), f"Lv.{_phantom.level}", "white", waves_font_24, "lm"
                )
                sh_temp.alpha_composite(ph_level_img, (128, 58))

                # 声骸分数背景
                ph_score_img = Image.new("RGBA", (100, 30), (255, 255, 255, 0))
                ph_score_img_draw = ImageDraw.Draw(ph_score_img)
                ph_score_img_draw.rounded_rectangle(
                    [0, 0, 100, 30], radius=8, fill=(186, 55, 42, int(0.8 * 255))
                )
                ph_score_img_draw.text(
                    (50, 13), f"{_score}分", "white", waves_font_24, "mm"
                )
                sh_temp.alpha_composite(ph_score_img, (223, 58))

                for index in range(0, _phantom.cost):
                    promote_icon = Image.open(TEXT_PATH / "promote_icon.png")
                    promote_icon = promote_icon.resize((30, 30))
                    sh_temp.alpha_composite(promote_icon, dest=(128 + 30 * index, 90))

                for index, _prop in enumerate(props):
                    oset = 55
                    prop_img = await get_attribute_prop(_prop.attributeName)
                    prop_img = prop_img.resize((40, 40))
                    sh_temp.alpha_composite(prop_img, (15, 167 + index * oset))
                    sh_temp_draw = ImageDraw.Draw(sh_temp)
                    name_color = "white"
                    num_color = "white"
                    if index > 1:
                        name_color, num_color = get_valid_color(
                            _prop.attributeName, _prop.attributeValue, calc.calc_temp
                        )
                    sh_temp_draw.text(
                        (60, 187 + index * oset),
                        f"{_prop.attributeName[:6]}",
                        name_color,
                        waves_font_24,
                        "lm",
                    )
                    sh_temp_draw.text(
                        (343, 187 + index * oset),
                        f"{_prop.attributeValue}",
                        num_color,
                        waves_font_24,
                        "rm",
                    )
            if is_draw:
                phantom_temp.alpha_composite(
                    sh_temp,
                    dest=(
                        30 + ((i + 1) % 3) * 385,
                        120 + ph_sum_value + ((i + 1) // 3) * 600,
                    ),
                )

        if phantom_score > 0:
            phantom_score = round(phantom_score, 2)
            _bg = get_total_score_bg(char_name, phantom_score, calc.calc_temp)
            sh_score_bg_c = Image.open(TEXT_PATH / f"sh_score_bg_{_bg}.png")
            score_temp = Image.new("RGBA", sh_score_bg_c.size)
            score_temp.alpha_composite(sh_score_bg_c)
            sh_score_c = Image.open(TEXT_PATH / f"sh_score_{_bg}.png")
            score_temp.alpha_composite(sh_score_c)
            score_temp_draw = ImageDraw.Draw(score_temp)

            score_temp_draw.text((180, 260), "声骸评级", GREY, waves_font_40, "mm")
            score_temp_draw.text(
                (180, 380), f"{phantom_score:.2f}分", "white", waves_font_40, "mm"
            )
            score_temp_draw.text((180, 440), "声骸评分", GREY, waves_font_40, "mm")
        else:
            abs_bg = Image.open(TEXT_PATH / "abs.png")
            score_temp = Image.new("RGBA", abs_bg.size)
            score_temp.alpha_composite(abs_bg)
            score_temp_draw = ImageDraw.Draw(score_temp)
            score_temp_draw.text((180, 130), "暂无", "white", waves_font_40, "mm")
            score_temp_draw.text((180, 380), "- 分", "white", waves_font_40, "mm")

        if is_draw:
            phantom_temp.alpha_composite(score_temp, dest=(30, 120 + ph_sum_value))

        shuxing = f"{role_detail.role.attributeName}伤害加成"
        for mi, m in enumerate(ph_sort_name):
            for ni, name_default in enumerate(m):
                name, default_value = name_default
                if name == "属性伤害加成":
                    value = calc.phantom_card.get(shuxing, default_value)
                    prop_img = await get_attribute_prop(shuxing)
                    name_color, _ = get_valid_color(shuxing, value, calc.calc_temp)
                    name = shuxing
                else:
                    value = calc.phantom_card.get(name, default_value)
                    prop_img = await get_attribute_prop(name)
                    name_color, _ = get_valid_color(name, value, calc.calc_temp)
                prop_img = prop_img.resize((40, 40))
                ph_bg = ph_0.copy() if ni % 2 == 0 else ph_1.copy()
                ph_bg.alpha_composite(prop_img, (20, 32))
                ph_bg_draw = ImageDraw.Draw(ph_bg)

                ph_bg_draw.text(
                    (70, 50), f"{name[:6]}", name_color, waves_font_24, "lm"
                )
                ph_bg_draw.text((343, 50), f"{value}", name_color, waves_font_24, "rm")

                phantom_temp.alpha_composite(ph_bg, (40 + mi * 370, 100 + ni * 50))

        ph_tips = ph_1.copy()
        ph_tips_draw = ImageDraw.Draw(ph_tips)

        ph_tips_draw.text((20, 50), "[提示]评分模板", "white", waves_font_24, "lm")
        ph_tips_draw.text(
            (350, 50), f"{calc.calc_temp['name']}", (255, 255, 0), waves_font_24, "rm"
        )
        # phantom_temp.alpha_composite(ph_tips, (40 + 2 * 370, 100 + 4 * 50))
        phantom_temp.alpha_composite(ph_tips, (40 + 2 * 370, 45))

        if change_command:
            phantom_temp_text = ImageDraw.Draw(phantom_temp)
            phantom_temp_text.text(
                (50, 90), f"{change_command}", SPECIAL_GOLD, waves_font_18, "lm"
            )

    # img.paste(phantom_temp, (0, 1320 + jineng_len), phantom_temp)
    return calc, phantom_temp


async def get_role_need(
    ev,
    char_id,
    ck,
    uid,
    char_name,
    waves_id=None,
    is_force_avatar=False,
    force_resource_id=None,
    is_online_user=True,
    is_limit_query=False,
    change_list_regex: Optional[str] = None,
):
    if waves_id:
        query_list = [char_id]
        if char_id in SPECIAL_CHAR:
            query_list = SPECIAL_CHAR.copy()[char_id]

        for char_id in query_list:
            role_detail_info = await waves_api.get_role_detail_info(
                char_id, waves_id, ck
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
            if role_detail_info["phantomData"]["cost"] == 0:
                role_detail_info["phantomData"]["equipPhantomList"] = None

            role_detail = RoleDetailData.model_validate(role_detail_info)

            avatar = await draw_char_with_ring(char_id)
            break
        else:
            return (
                None,
                f"[鸣潮] 特征码[{waves_id}] \n无法获取【{char_name}】角色信息，请在库街区展示此角色！\n",
            )
    else:
        avatar = await draw_pic_with_ring(ev, is_force_avatar, force_resource_id)
        all_role_detail: Optional[Dict[str, RoleDetailData]] = (
            await get_all_roleid_detail_info(uid)
        )

        if char_id in SPECIAL_CHAR:
            query_list = SPECIAL_CHAR.copy()[char_id]
        else:
            query_list = [char_id]

        for temp_char_id in query_list:
            if all_role_detail and temp_char_id in all_role_detail:
                role_detail: RoleDetailData = all_role_detail[temp_char_id]
                break
        else:
            if is_limit_query:
                return (
                    None,
                    f"[鸣潮] 未找到【{char_name}】角色极限面板信息，请等待适配!\n",
                )
            elif is_online_user and not change_list_regex:
                return (
                    None,
                    f"[鸣潮] 未找到【{char_name}】角色信息, 请先使用[{PREFIX}刷新面板]进行刷新!\n",
                )
            else:
                # 未上线的角色，构造一个数据
                gen_role_detail = await generate_online_role_detail(char_id)
                if not gen_role_detail:
                    return (
                        None,
                        f"[鸣潮] 未找到【{char_name}】角色信息, 请先使用[{PREFIX}刷新面板]进行刷新!\n",
                    )
                role_detail = gen_role_detail

    return avatar, role_detail


async def draw_fixed_img(img, avatar, account_info, role_detail):
    # 头像部分
    avatar_ring = Image.open(TEXT_PATH / "avatar_ring.png")

    img.paste(avatar, (45, 20), avatar)
    avatar_ring = avatar_ring.resize((180, 180))
    img.paste(avatar_ring, (55, 30), avatar_ring)

    base_info_bg = Image.open(TEXT_PATH / "base_info_bg.png")
    base_info_draw = ImageDraw.Draw(base_info_bg)
    base_info_draw.text(
        (275, 120), f"{account_info.name[:7]}", "white", waves_font_30, "lm"
    )
    base_info_draw.text(
        (226, 173), f"特征码:  {account_info.id}", GOLD, waves_font_25, "lm"
    )
    img.paste(base_info_bg, (35, -30), base_info_bg)

    if account_info.is_full:
        title_bar = Image.open(TEXT_PATH / "title_bar.png")
        title_bar_draw = ImageDraw.Draw(title_bar)
        title_bar_draw.text((510, 125), "账号等级", GREY, waves_font_26, "mm")
        title_bar_draw.text(
            (510, 78), f"Lv.{account_info.level}", "white", waves_font_42, "mm"
        )

        title_bar_draw.text((660, 125), "世界等级", GREY, waves_font_26, "mm")
        title_bar_draw.text(
            (660, 78), f"Lv.{account_info.worldLevel}", "white", waves_font_42, "mm"
        )

        logo_img = get_small_logo(2)
        title_bar.alpha_composite(logo_img, dest=(780, 65))
        img.paste(title_bar, (200, 15), title_bar)

    # 左侧pile部分
    is_custom, role_pile = await get_role_pile(role_detail.role.roleId, True)
    char_mask = Image.open(TEXT_PATH / "char_mask.png")
    char_fg = Image.open(TEXT_PATH / "char_fg.png")

    role_attribute = await get_attribute(role_detail.role.attributeName)
    role_attribute = role_attribute.resize((50, 50)).convert("RGBA")
    char_fg.paste(role_attribute, (434, 112), role_attribute)
    weapon_type = await get_weapon_type(role_detail.role.weaponTypeName)
    weapon_type = weapon_type.resize((40, 40)).convert("RGBA")
    char_fg.paste(weapon_type, (439, 182), weapon_type)

    char_fg_image = ImageDraw.Draw(char_fg)
    roleName = role_detail.role.roleName
    if "漂泊者" in roleName:
        roleName = "漂泊者"

    draw_text_with_shadow(
        char_fg_image,
        f"{roleName} Lv.{role_detail.role.level}",
        285,
        867,
        waves_font_50,
        anchor="mm",
    )

    role_pile_image = Image.new("RGBA", (560, 1000))

    role_pile = resize_and_center_image(role_pile, is_custom=is_custom)
    role_pile_image.paste(
        role_pile,
        ((560 - role_pile.size[0]) // 2, (1000 - role_pile.size[1]) // 2),
        role_pile,
    )
    img.paste(role_pile_image, (25, 170), char_mask)
    img.paste(char_fg, (25, 170), char_fg)


def resize_and_center_image(
    image, output_size=(560, 1000), background_color=(255, 255, 255, 0), is_custom=False
):
    """
    根据输入的图片，调整其尺寸以尽量填充目标尺寸，并保持居中。
    若宽度过长或高度过长，会根据图片的比例自动调整，以保持居中并尽量维持固定尺寸（560x1000）。

    :param image: 原始图片对象
    :param output_size: 输出图片大小 (宽度, 高度)
    :param background_color: 填充背景的颜色 (默认为透明)
    :param is_custom: 是否为自定义面板，决定是否需要调整图片
    :return: 调整后的图片对象
    """
    # 如果不需要自定义调整，直接返回原图
    if not is_custom:
        return image

    image = image.copy()

    # 获取原始图片的宽度和高度
    img_width, img_height = image.size
    target_width, target_height = output_size

    # 如果图片的宽度大于高度，则根据宽度缩放图片
    if img_width > img_height:
        scale_factor = target_width / img_width
        new_width = target_width
        new_height = int(img_height * scale_factor)
    else:
        scale_factor = target_height / img_height
        new_width = int(img_width * scale_factor)
        new_height = target_height

    image = image.resize((new_width, new_height))

    result_image = Image.new("RGBA", output_size, background_color)

    # 计算粘贴位置，居中对齐
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2

    result_image.paste(image, (paste_x, paste_y), image)

    return result_image


async def draw_char_detail_img(
    ev: Event,
    uid: str,
    char: str,
    user_id,
    waves_id: Optional[str] = None,
    need_convert_img=True,
    is_force_avatar=False,
    change_list_regex=None,
    is_limit_query=False,
):
    char, damageId = parse_text_and_number(char)

    char_id = char_name_to_char_id(char)
    if not char_id:
        return (
            f"[鸣潮] 角色名【{char}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
        )

    char_name = alias_to_char_name(char)

    damageDetail = DamageDetailRegister.find_class(char_id)
    ph_sum_value = 250
    jineng_len = 180
    dd_len = 0
    isDraw = False if damageId and damageDetail else True
    echo_list = 1400 if isDraw else 170
    if damageDetail and isDraw:
        dd_len = 60 + (len(damageDetail) + 1) * 60

    damage_calc = None
    if not isDraw:
        for dindex, dd in enumerate(damageDetail):  # type: ignore
            if dindex + 1 == int(damageId):  # type: ignore
                damage_calc = dd
                break
        else:
            return f"[鸣潮] 角色【{char_name}】未找到该伤害类型[{damageId}], 请先检查输入是否正确！\n"
    else:
        if damageId and not damageDetail:
            return f"[鸣潮] 角色【{char_name}】暂不支持伤害计算！\n"

    is_online_user = False
    ck = ""
    if not is_limit_query:
        _, ck = await waves_api.get_ck_result(uid, user_id, ev.bot_id)
        if not ck:
            return hint.error_reply(WAVES_CODE_102)

        online_list = await waves_api.get_online_list_role(ck)
        if online_list.success and online_list.data:
            online_list_role_model = OnlineRoleList.model_validate(online_list.data)
            online_role_map = {str(i.roleId): i for i in online_list_role_model}
            if char_id in online_role_map:
                is_online_user = True

    # 账户数据
    if waves_id:
        uid = waves_id

    if not is_limit_query:
        account_info = await waves_api.get_base_info(uid, ck)
        if not account_info.success:
            return account_info.throw_msg()
        account_info = AccountBaseInfo.model_validate(account_info.data)
        force_resource_id = None
    else:
        account_info = AccountBaseInfo.model_validate(
            {
                "name": "库洛交个朋友",
                "id": uid,
                "level": 100,
                "worldLevel": 10,
                "creatTime": 1739375719,
            }
        )
        force_resource_id = char_id
    # 获取数据
    avatar, role_detail = await get_role_need(
        ev,
        char_id,
        ck,
        uid,
        char_name,
        waves_id,
        is_force_avatar,
        force_resource_id,
        is_online_user,
        is_limit_query,
        change_list_regex,
    )
    if isinstance(role_detail, str):
        return role_detail

    change_command = ""
    oneRank: Optional[OneRankResponse] = None
    enemy_detail: Optional[EnemyDetailData] = EnemyDetailData()
    if change_list_regex:
        temp = copy.deepcopy(role_detail)
        try:
            role_detail, change_command = await change_role_detail(
                uid, ck, role_detail, enemy_detail, change_list_regex
            )
        except Exception as e:
            logger.exception("角色数据转换错误", e)
            role_detail = temp
    else:
        if not is_limit_query:
            # 非极限查询时，获取评分排名
            oneRank = await get_one_rank(
                OneRankRequest(char_id=int(char_id), waves_id=uid)
            )
            if oneRank and len(oneRank.data) > 0:
                dd_len += 60 * 2

    # 声骸
    calc, phantom_temp = await ph_card_draw(
        ph_sum_value, role_detail, isDraw, change_command, enemy_detail
    )
    calc.role_card = calc.enhance_summation_card_value(calc.phantom_card)

    damage_calc_img = None
    if (
        damage_calc
        and damageDetail
        and role_detail.phantomData
        and role_detail.phantomData.equipPhantomList
    ):
        damage_title = damage_calc["title"]
        # damageAttribute = card_sort_map_to_attribute(card_map)
        calc.damageAttribute = calc.card_sort_map_to_attribute(calc.role_card)
        damageAttributeTemp = copy.deepcopy(calc.damageAttribute)
        crit_damage, expected_damage = damage_calc["func"](
            damageAttributeTemp, role_detail
        )
        logger.debug(f"{char_name}-{damage_title} 暴击伤害: {crit_damage}")
        logger.debug(f"{char_name}-{damage_title} 期望伤害: {expected_damage}")
        logger.debug(f"{char_name}-{damage_title} 属性值: {damageAttributeTemp}")

        damage_high = 100 + (len(damageAttributeTemp.effect) + 3) * 60
        damage_calc_img = Image.new("RGBA", (1200, damage_high))

        damage_title_bg = damage_bar1.copy()
        damage_title_bg_draw = ImageDraw.Draw(damage_title_bg)
        damage_title_bg_draw.text(
            (400, 50), "伤害类型", SPECIAL_GOLD, waves_font_24, "rm"
        )
        damage_title_bg_draw.text(
            (700, 50), "暴击伤害", SPECIAL_GOLD, waves_font_24, "mm"
        )
        damage_title_bg_draw.text(
            (1000, 50), "期望伤害", SPECIAL_GOLD, waves_font_24, "mm"
        )
        damage_calc_img.alpha_composite(damage_title_bg, dest=(0, 10))

        damage_bar = damage_bar2.copy()
        damage_bar_draw = ImageDraw.Draw(damage_bar)
        damage_bar_draw.text((400, 50), f"{damage_title}", "white", waves_font_24, "rm")
        if crit_damage and expected_damage:
            damage_bar_draw.text(
                (700, 50), f"{crit_damage}", "white", waves_font_24, "mm"
            )
            damage_bar_draw.text(
                (1000, 50), f"{expected_damage}", "white", waves_font_24, "mm"
            )
        else:
            damage_bar_draw.text(
                (850, 50), f"{expected_damage}", "white", waves_font_24, "mm"
            )
        damage_calc_img.alpha_composite(damage_bar, dest=(0, 70))

        damage_title_bg = damage_bar1.copy()
        damage_title_bg_draw = ImageDraw.Draw(damage_title_bg)
        damage_title_bg_draw.text((600, 50), "buff列表", "white", waves_font_24, "mm")
        damage_calc_img.alpha_composite(damage_title_bg, dest=(0, 130))

        for dindex, effect in enumerate(damageAttributeTemp.effect):
            buff_name = effect.element_msg
            buff_value = effect.element_value
            damage_bar = damage_bar2.copy() if dindex % 2 == 0 else damage_bar1.copy()
            damage_bar_draw = ImageDraw.Draw(damage_bar)
            damage_bar_draw.text(
                (400, 50), f"{buff_name}", "white", waves_font_24, "rm"
            )
            damage_bar_draw.text(
                (800, 50), f"{buff_value}", "white", waves_font_24, "mm"
            )
            damage_calc_img.alpha_composite(
                damage_bar, dest=(0, 10 + (dindex + 3) * 60)
            )

        dd_len += damage_calc_img.size[1]

    # 创建背景
    img = await get_card_bg(
        1200, 1250 + echo_list + ph_sum_value + jineng_len + dd_len, "bg3"
    )
    # 固定位置
    await draw_fixed_img(img, avatar, account_info, role_detail)

    # 声骸
    img.paste(phantom_temp, (0, 1320 + jineng_len), phantom_temp)

    if damage_calc_img:
        img.alpha_composite(
            damage_calc_img, (0, img.size[1] - 10 - damage_calc_img.size[1])
        )

    # 右侧属性
    right_image_temp = Image.new("RGBA", (600, 1100))

    # 武器banner
    banner2 = Image.open(TEXT_PATH / "banner2.png")
    right_image_temp.alpha_composite(banner2, dest=(0, 550))

    # 右侧属性-武器
    weapon_bg = Image.open(TEXT_PATH / "weapon_bg.png")
    weapon_bg_temp = Image.new("RGBA", weapon_bg.size)
    weapon_bg_temp.alpha_composite(weapon_bg, dest=(0, 0))

    weaponData: WeaponData = role_detail.weaponData

    weapon_icon = await get_square_weapon(weaponData.weapon.weaponId)
    weapon_icon = crop_center_img(weapon_icon, 110, 110)
    weapon_icon_bg = get_weapon_icon_bg(weaponData.weapon.weaponStarLevel)
    weapon_icon_bg.paste(weapon_icon, (10, 20), weapon_icon)

    weapon_bg_temp_draw = ImageDraw.Draw(weapon_bg_temp)
    weapon_bg_temp_draw.text(
        (200, 30), f"{weaponData.weapon.weaponName}", SPECIAL_GOLD, waves_font_40, "lm"
    )
    weapon_bg_temp_draw.text(
        (203, 75), f"Lv.{weaponData.level}/90", "white", waves_font_30, "lm"
    )

    _x = 220 + 43 * len(weaponData.weapon.weaponName)
    _y = 37
    wrc_fill = WEAPON_RESONLEVEL_COLOR[weaponData.resonLevel] + (int(0.8 * 255),)  # type: ignore
    weapon_bg_temp_draw.rounded_rectangle(
        [_x - 15, _y - 15, _x + 50, _y + 15], radius=7, fill=wrc_fill
    )

    weapon_bg_temp_draw.text(
        (_x, _y), f"精{weaponData.resonLevel}", "white", waves_font_24, "lm"
    )

    weapon_breach = get_breach(weaponData.breach, weaponData.level)
    for i in range(0, weapon_breach):  # type: ignore
        promote_icon = Image.open(TEXT_PATH / "promote_icon.png")
        weapon_bg_temp.alpha_composite(promote_icon, dest=(200 + 40 * i, 100))

    weapon_bg_temp.alpha_composite(weapon_icon_bg, dest=(45, 0))

    weapon_detail: WavesWeaponResult = get_weapon_detail(
        weaponData.weapon.weaponId,
        weaponData.level,
        weaponData.breach,
        weaponData.resonLevel,
    )
    stats_main = await get_attribute_prop(weapon_detail.stats[0]["name"])
    stats_main = stats_main.resize((40, 40))
    weapon_bg_temp.alpha_composite(stats_main, (65, 187))
    weapon_bg_temp_draw.text(
        (130, 207), f"{weapon_detail.stats[0]['name']}", "white", waves_font_30, "lm"
    )
    weapon_bg_temp_draw.text(
        (500, 207), f"{weapon_detail.stats[0]['value']}", "white", waves_font_30, "rm"
    )
    stats_sub = await get_attribute_prop(weapon_detail.stats[1]["name"])
    stats_sub = stats_sub.resize((40, 40))
    weapon_bg_temp.alpha_composite(stats_sub, (65, 237))
    weapon_bg_temp_draw.text(
        (130, 257), f"{weapon_detail.stats[1]['name']}", "white", waves_font_30, "lm"
    )
    weapon_bg_temp_draw.text(
        (500, 257), f"{weapon_detail.stats[1]['value']}", "white", waves_font_30, "rm"
    )

    right_image_temp.alpha_composite(weapon_bg_temp, dest=(0, 650))

    # 命座部分
    mz_temp = Image.new("RGBA", (1200, 300))

    shuxing_color = WAVES_SHUXING_MAP[role_detail.role.attributeName]  # type: ignore
    for i, _mz in enumerate(role_detail.chainList):
        mz_bg = Image.open(TEXT_PATH / "mz_bg.png")
        mz_bg_temp = Image.new("RGBA", mz_bg.size)
        mz_bg_temp_draw = ImageDraw.Draw(mz_bg_temp)
        chain = await get_chain_img(role_detail.role.roleId, _mz.order, _mz.iconUrl)  # type: ignore
        chain = chain.resize((100, 100))
        mz_bg.paste(chain, (95, 75), chain)
        mz_bg_temp.alpha_composite(mz_bg, dest=(0, 0))
        if _mz.unlocked:
            mz_bg_temp = await change_color(mz_bg_temp, shuxing_color)

        name = re.sub(r'[",，]+', "", _mz.name) if _mz.name else ""
        if len(name) >= 8:
            mz_bg_temp_draw.text((147, 230), f"{name}", "white", waves_font_16, "mm")
        else:
            mz_bg_temp_draw.text((147, 230), f"{name}", "white", waves_font_20, "mm")

        if not _mz.unlocked:
            mz_bg_temp = ImageEnhance.Brightness(mz_bg_temp).enhance(0.3)
        mz_temp.alpha_composite(mz_bg_temp, dest=(i * 190, 0))

    img.paste(mz_temp, (0, 1080 + jineng_len), mz_temp)

    if (
        isDraw
        and damageDetail
        and role_detail.phantomData
        and role_detail.phantomData.equipPhantomList
    ):
        # damageAttribute = card_sort_map_to_attribute(card_map)
        calc.damageAttribute = calc.card_sort_map_to_attribute(calc.role_card)
        damage_title_bg = damage_bar1.copy()
        damage_title_bg_draw = ImageDraw.Draw(damage_title_bg)
        damage_title_bg_draw.text(
            (400, 50), "伤害类型", SPECIAL_GOLD, waves_font_24, "rm"
        )
        damage_title_bg_draw.text(
            (700, 50), "暴击伤害", SPECIAL_GOLD, waves_font_24, "mm"
        )
        damage_title_bg_draw.text(
            (1000, 50), "期望伤害", SPECIAL_GOLD, waves_font_24, "mm"
        )
        img.alpha_composite(damage_title_bg, dest=(0, 2600 + ph_sum_value + jineng_len))
        for dindex, damage_temp in enumerate(damageDetail):
            damage_title = damage_temp["title"]
            damageAttributeTemp = copy.deepcopy(calc.damageAttribute)
            crit_damage, expected_damage = damage_temp["func"](
                damageAttributeTemp, role_detail
            )
            logger.debug(f"{char_name}-{damage_title} 暴击伤害: {crit_damage}")
            logger.debug(f"{char_name}-{damage_title} 期望伤害: {expected_damage}")
            logger.debug(f"{char_name}-{damage_title} 属性值: {damageAttributeTemp}")

            damage_bar = damage_bar2.copy() if dindex % 2 == 0 else damage_bar1.copy()
            damage_bar_draw = ImageDraw.Draw(damage_bar)
            damage_bar_draw.text(
                (400, 50), f"{damage_title}", "white", waves_font_24, "rm"
            )
            if crit_damage and expected_damage:
                damage_bar_draw.text(
                    (700, 50), f"{crit_damage}", "white", waves_font_24, "mm"
                )
                damage_bar_draw.text(
                    (1000, 50), f"{expected_damage}", "white", waves_font_24, "mm"
                )
            else:
                damage_bar_draw.text(
                    (850, 50), f"{expected_damage}", "white", waves_font_24, "mm"
                )
            img.alpha_composite(
                damage_bar,
                dest=(0, 2600 + ph_sum_value + jineng_len + (dindex + 1) * 60),
            )

        if oneRank and len(oneRank.data) > 0:
            dindex += 1
            damage_bar = damage_bar2.copy() if dindex % 2 == 0 else damage_bar1.copy()
            damage_bar_draw = ImageDraw.Draw(damage_bar)
            damage_bar_draw = ImageDraw.Draw(damage_bar)
            damage_bar_draw.text(
                (400, 50),
                "评分排名",
                "white",
                waves_font_24,
                "rm",
            )
            damage_bar_draw.text(
                (850, 50),
                f"{oneRank.data[0].rank}",
                SPECIAL_GOLD,
                waves_font_24,
                "mm",
            )
            img.alpha_composite(
                damage_bar,
                dest=(0, 2600 + ph_sum_value + jineng_len + (dindex + 1) * 60),
            )

            dindex += 1
            damage_bar = damage_bar2.copy() if dindex % 2 == 0 else damage_bar1.copy()
            damage_bar_draw = ImageDraw.Draw(damage_bar)
            damage_bar_draw = ImageDraw.Draw(damage_bar)
            damage_bar_draw.text(
                (400, 50),
                "伤害排名",
                "white",
                waves_font_24,
                "rm",
            )
            damage_bar_draw.text(
                (850, 50),
                f"{oneRank.data[1].rank}",
                SPECIAL_GOLD,
                waves_font_24,
                "mm",
            )
            img.alpha_composite(
                damage_bar,
                dest=(0, 2600 + ph_sum_value + jineng_len + (dindex + 1) * 60),
            )

    banner1 = Image.open(TEXT_PATH / "banner4.png")
    right_image_temp.alpha_composite(banner1, dest=(0, 0))
    sh_bg = Image.open(TEXT_PATH / "prop_bg.png")
    sh_bg_draw = ImageDraw.Draw(sh_bg)

    shuxing = f"{role_detail.role.attributeName}伤害加成"
    for index, name_default in enumerate(card_sort_name):
        name, default_value = name_default
        if name == "属性伤害加成":
            value = calc.role_card.get(shuxing, default_value)
            prop_img = await get_attribute_prop(shuxing)
            name_color, _ = get_valid_color(shuxing, value, calc.calc_temp)
            name = shuxing
        else:
            value = calc.role_card.get(name, default_value)
            prop_img = await get_attribute_prop(name)
            name_color, _ = get_valid_color(name, value, calc.calc_temp)

        prop_img = prop_img.resize((40, 40))
        sh_bg.alpha_composite(prop_img, (60, 40 + index * 55))
        sh_bg_draw.text(
            (120, 58 + index * 55), f"{name[:6]}", name_color, waves_font_24, "lm"
        )
        sh_bg_draw.text(
            (530, 58 + index * 55), f"{value}", name_color, waves_font_24, "rm"
        )

    right_image_temp.alpha_composite(sh_bg, dest=(0, 80))
    img.paste(right_image_temp, (570, 200), right_image_temp)

    # 技能
    skill_bar = Image.open(TEXT_PATH / "skill_bar.png")
    skill_bg_1 = Image.open(TEXT_PATH / "skill_bg.png")

    temp_i = 0
    for _, _skill in enumerate(role_detail.get_skill_list()):
        if _skill.skill.type == "延奏技能":
            continue
        skill_bg = skill_bg_1.copy()
        # logger.debug(f"{char_name}-{_skill.skill.name}")
        skill_img = await get_skill_img(
            role_detail.role.roleId, _skill.skill.name, _skill.skill.iconUrl
        )
        skill_img = skill_img.resize((70, 70))
        skill_bg.paste(skill_img, (57, 65), skill_img)

        skill_bg_draw = ImageDraw.Draw(skill_bg)
        skill_bg_draw.text(
            (150, 83), f"{_skill.skill.type}", "white", waves_font_25, "lm"
        )
        skill_bg_draw.text(
            (150, 113), f"Lv.{_skill.level}", "white", waves_font_25, "lm"
        )

        skill_bg_temp = Image.new("RGBA", skill_bg.size)
        skill_bg_temp = Image.alpha_composite(skill_bg_temp, skill_bg)

        _x = 20 + temp_i * 215
        _y = -20
        skill_bar.alpha_composite(skill_bg_temp, dest=(_x, _y))
        temp_i += 1
    img.alpha_composite(skill_bar, dest=(0, 1150))

    img = add_footer(img)
    if need_convert_img:
        img = await convert_img(img)
    return img


async def draw_char_score_img(
    ev: Event, uid: str, char: str, user_id: str, waves_id: Optional[str] = None
):
    char, damageId = parse_text_and_number(char)

    char_id = char_name_to_char_id(char)
    if not char_id:
        return (
            f"[鸣潮] 角色名【{char}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
        )
    char_name = alias_to_char_name(char)
    _, ck = await waves_api.get_ck_result(uid, user_id, ev.bot_id)
    if not ck:
        return hint.error_reply(WAVES_CODE_102)

    # 账户数据
    if waves_id:
        uid = waves_id
    account_info = await waves_api.get_base_info(uid, ck)
    if not account_info.success:
        return account_info.throw_msg()
    account_info = AccountBaseInfo.model_validate(account_info.data)
    # 获取数据
    avatar, role_detail = await get_role_need(ev, char_id, ck, uid, char_name, waves_id)
    if isinstance(role_detail, str):
        return role_detail

    # 创建背景
    img = await get_card_bg(1200, 3380, "bg3")
    # 固定位置
    await draw_fixed_img(img, avatar, account_info, role_detail)

    # 声骸属性
    char_id = role_detail.role.roleId
    char_name = role_detail.role.roleName

    phantom_temp = Image.new("RGBA", (1200, 1380))
    right_image_temp = Image.new("RGBA", (600, 1100))
    introduce_temp = Image.new("RGBA", (1500, 880), (0, 0, 0, 0))

    ph_0 = Image.open(TEXT_PATH / "ph_0.png")
    ph_1 = Image.open(TEXT_PATH / "ph_1.png")
    # phantom_sum_value = {}
    calc: WuWaCalc = WuWaCalc(role_detail)
    if role_detail.phantomData and role_detail.phantomData.equipPhantomList:
        equipPhantomList = role_detail.phantomData.equipPhantomList
        phantom_score = 0

        calc.phantom_pre = calc.prepare_phantom()
        calc.phantom_card = calc.enhance_summation_phantom_value(calc.phantom_pre)
        calc.calc_temp = get_calc_map(
            calc.phantom_card,
            role_detail.role.roleName,
            role_detail.role.roleId,
        )

        for i, _phantom in enumerate(equipPhantomList):
            sh_temp = Image.new("RGBA", (600, 1100))
            sh_temp_draw = ImageDraw.Draw(sh_temp)
            sh_bg = Image.open(TEXT_PATH / "sh_bg.png")
            sh_temp.alpha_composite(sh_bg, dest=(0, 0))
            if _phantom and _phantom.phantomProp:
                props = _phantom.get_props()
                _score, _bg = calc_phantom_score(
                    char_id, props, _phantom.cost, calc.calc_temp
                )

                phantom_score += _score
                sh_title = Image.open(TEXT_PATH / f"sh_title_{_bg}.png")

                sh_temp.alpha_composite(sh_title, dest=(0, 0))

                phantom_icon = await get_phantom_img(
                    _phantom.phantomProp.phantomId, _phantom.phantomProp.iconUrl
                )
                fetter_icon = await get_attribute_effect(_phantom.fetterDetail.name)
                fetter_icon = fetter_icon.resize((50, 50))
                phantom_icon.alpha_composite(fetter_icon, dest=(205, 0))
                phantom_icon = phantom_icon.resize((100, 100))
                sh_temp.alpha_composite(phantom_icon, dest=(20, 20))
                phantomName = (
                    _phantom.phantomProp.name.replace("·", " ")
                    .replace("（", " ")
                    .replace("）", "")
                )
                short_name = get_short_name(_phantom.phantomProp.phantomId, phantomName)
                sh_temp_draw.text(
                    (130, 40), f"{short_name}", SPECIAL_GOLD, waves_font_28, "lm"
                )

                # 声骸等级背景
                ph_level_img = Image.new("RGBA", (84, 30), (255, 255, 255, 0))
                ph_level_img_draw = ImageDraw.Draw(ph_level_img)
                ph_level_img_draw.rounded_rectangle(
                    [0, 0, 84, 30], radius=8, fill=(0, 0, 0, int(0.8 * 255))
                )
                ph_level_img_draw.text(
                    (8, 13), f"Lv.{_phantom.level}", "white", waves_font_24, "lm"
                )
                sh_temp.alpha_composite(ph_level_img, (128, 58))

                # 声骸分数背景
                ph_score_img = Image.new("RGBA", (100, 30), (255, 255, 255, 0))
                ph_score_img_draw = ImageDraw.Draw(ph_score_img)
                ph_score_img_draw.rounded_rectangle(
                    [0, 0, 100, 30], radius=8, fill=(186, 55, 42, int(0.8 * 255))
                )
                ph_score_img_draw.text(
                    (50, 13), f"{_score}分", "white", waves_font_24, "mm"
                )
                sh_temp.alpha_composite(ph_score_img, (228, 58))

                for index in range(0, _phantom.cost):
                    promote_icon = Image.open(TEXT_PATH / "promote_icon.png")
                    promote_icon = promote_icon.resize((30, 30))
                    sh_temp.alpha_composite(promote_icon, dest=(128 + 30 * index, 90))

                for index, _prop in enumerate(props):
                    oset = 55
                    prop_img = await get_attribute_prop(_prop.attributeName)
                    prop_img = prop_img.resize((40, 40))
                    # sh_temp.alpha_composite(prop_img, (15, 167 + index * oset))
                    sh_temp_draw = ImageDraw.Draw(sh_temp)
                    name_color = "white"
                    num_color = "white"
                    if index > 1:
                        name_color, num_color = get_valid_color(
                            _prop.attributeName, _prop.attributeValue, calc.calc_temp
                        )
                    sh_temp_draw.text(
                        (15, 187 + index * oset),
                        f"{_prop.attributeName[:6]}",
                        name_color,
                        waves_font_24,
                        "lm",
                    )
                    sh_temp_draw.text(
                        (273, 187 + index * oset),
                        f"{_prop.attributeValue}",
                        num_color,
                        waves_font_24,
                        "rm",
                    )

                    score, final_score = calc_phantom_entry(
                        index,
                        _prop,
                        _phantom.cost,
                        calc.calc_temp,
                        role_detail.role.attributeName or "",
                    )
                    score_color = WAVES_MOONLIT
                    if final_score > 0:
                        score_color = WAVES_FREEZING
                    sh_temp_draw.text(
                        (343, 191 + index * oset),
                        f"{final_score}分",
                        score_color,
                        waves_font_18,
                        "rm",
                    )

                max_score, _ = get_max_score(_phantom.cost, calc.calc_temp)
                sh_temp_draw.text(
                    (343, 191 + 7 * 55),
                    f"C{_phantom.cost}最高分(未对齐):{max_score}分",
                    SPECIAL_GOLD,
                    waves_font_18,
                    "rm",
                )

                phantom_temp.alpha_composite(
                    sh_temp, dest=(30 + ((i + 1) % 3) * 385, 120 + ((i + 1) // 3) * 630)
                )

        if phantom_score > 0:
            phantom_score = round(phantom_score, 2)
            _bg = get_total_score_bg(char_name, phantom_score, calc.calc_temp)
            sh_score_bg_c = Image.open(TEXT_PATH / f"sh_score_bg_{_bg}.png")
            score_temp = Image.new("RGBA", sh_score_bg_c.size)
            score_temp.alpha_composite(sh_score_bg_c)
            sh_score_c = Image.open(TEXT_PATH / f"sh_score_{_bg}.png")
            score_temp.alpha_composite(sh_score_c)
            score_temp_draw = ImageDraw.Draw(score_temp)

            score_temp_draw.text((180, 260), "声骸评级", GREY, waves_font_40, "mm")
            score_temp_draw.text(
                (180, 380), f"{phantom_score:.2f}分", "white", waves_font_40, "mm"
            )
            score_temp_draw.text((180, 440), "声骸评分", GREY, waves_font_40, "mm")
        else:
            abs_bg = Image.open(TEXT_PATH / "abs.png")
            score_temp = Image.new("RGBA", abs_bg.size)
            score_temp.alpha_composite(abs_bg)
            score_temp_draw = ImageDraw.Draw(score_temp)
            score_temp_draw.text((180, 130), "暂无", "white", waves_font_40, "mm")
            score_temp_draw.text((180, 380), "- 分", "white", waves_font_40, "mm")

        phantom_temp.alpha_composite(score_temp, dest=(30, 120))

        shuxing = f"{role_detail.role.attributeName}伤害加成"
        for mi, m in enumerate(ph_sort_name):
            for ni, name_default in enumerate(m):
                name, default_value = name_default
                if name == "属性伤害加成":
                    value = calc.phantom_card.get(shuxing, default_value)
                    prop_img = await get_attribute_prop(shuxing)
                    name_color, _ = get_valid_color(shuxing, value, calc.calc_temp)
                    name = shuxing
                else:
                    value = calc.phantom_card.get(name, default_value)
                    prop_img = await get_attribute_prop(name)
                    name_color, _ = get_valid_color(name, value, calc.calc_temp)
                prop_img = prop_img.resize((40, 40))
                ph_bg = ph_0.copy() if ni % 2 == 0 else ph_1.copy()
                ph_bg.alpha_composite(prop_img, (20, 32))
                ph_bg_draw = ImageDraw.Draw(ph_bg)

                ph_bg_draw.text(
                    (70, 50), f"{name[:6]}", name_color, waves_font_24, "lm"
                )
                ph_bg_draw.text((350, 50), f"{value}", name_color, waves_font_24, "rm")

                right_image_temp.alpha_composite(
                    ph_bg.resize((500, 125)), (0, (ni + mi * 4) * 70)
                )

        ph_tips = ph_1.copy()
        ph_tips_draw = ImageDraw.Draw(ph_tips)
        ph_tips_draw.text((20, 50), "[提示]评分模板", "white", waves_font_24, "lm")
        ph_tips_draw.text(
            (350, 50), f"{calc.calc_temp['name']}", (255, 255, 0), waves_font_24, "rm"
        )
        phantom_temp.alpha_composite(ph_tips, (40 + 2 * 370, 45))

        # 简介数据
        weight_list_temp = weight_list.copy()
        entry_type_list = weight_list_temp[0].split(",")[1:]
        main_props = calc.calc_temp["main_props"]
        sub_pros = calc.calc_temp["sub_props"]
        skill_weight = calc.calc_temp["skill_weight"]
        for i, entry in enumerate(weight_list_temp[1:], start=1):
            entry_list = []
            if entry == "属性伤害加成":
                entry_list.append(f"{shuxing}")
            elif "%" in entry:
                entry_list.append(entry.replace("%", "百分比"))
            else:
                entry_list.append(entry)
            for entry_type in entry_type_list:
                if "主词条权重" in entry_type:
                    cost = re.search(r"C(\d+)主词条权重", entry_type).group(1)  # type: ignore
                    pros_temp = main_props.get(str(cost))
                else:
                    pros_temp = sub_pros

                if entry == "普攻伤害加成":
                    value = pros_temp.get("技能伤害加成", 0) * skill_weight[0]
                elif entry == "重击伤害加成":
                    value = pros_temp.get("技能伤害加成", 0) * skill_weight[1]
                elif entry == "共鸣技能伤害加成":
                    value = pros_temp.get("技能伤害加成", 0) * skill_weight[2]
                elif entry == "共鸣解放伤害加成":
                    value = pros_temp.get("技能伤害加成", 0) * skill_weight[3]
                else:
                    value = pros_temp.get(entry, 0)

                if value == 0:
                    value = "-"
                else:
                    value = f"{value:.3f}"
                entry_list.append(value)
            weight_list_temp[i] = ",".join(entry_list)

        await draw_weight(
            introduce_temp, role_detail.role.roleName, weight_list_temp, calc.calc_temp
        )

    char_bg = Image.open(TEXT_PATH / "char.png")
    img.paste(char_bg, (1100, 220), char_bg)
    img.paste(phantom_temp, (0, 1050), phantom_temp)
    img.paste(right_image_temp, (605, 225), right_image_temp)
    img.alpha_composite(introduce_temp, (0, 2400))

    img = add_footer(img)
    img = await convert_img(img)
    return img


async def draw_weight(image, role_name, weight_list_temp, calc_temp):
    draw = ImageDraw.Draw(image)
    draw.rectangle([10, 10, 1490, 870], fill=(0, 0, 0, int(0.7 * 255)))

    # 设置表格参数
    cell_width = 230
    cell_height = 40
    start_x, start_y = 25, 80

    # 绘制表格
    for i, row in enumerate(weight_list_temp):
        for j, cell in enumerate(row.split(",")):
            x = start_x + j * cell_width
            y = start_y + i * cell_height

            # 绘制单元格背景
            if i == 0:  # 标题行
                draw.rectangle(
                    [x, y, x + cell_width, y + cell_height], fill=(0, 0, 0, 90)
                )
            elif i % 2 == 1:  # 奇数行
                draw.rectangle(
                    [x, y, x + cell_width, y + cell_height], fill=(255, 255, 255, 30)
                )
            else:  # 偶数行
                draw.rectangle(
                    [x, y, x + cell_width, y + cell_height], fill=(0, 0, 0, 90)
                )

            # 绘制文字
            font = waves_font_24 if i == 0 else waves_font_20
            left, top, right, bottom = font.getbbox(cell)
            text_width = right - left
            text_height = bottom - top
            text_x = x + (cell_width - text_width) / 2
            text_y = y + (cell_height - text_height) / 2

            if i == 0:
                color = "white"
            else:
                if j == 0:
                    name_color, _ = get_valid_color(cell, "", calc_temp)
                    color = name_color
                else:
                    color = "white"
            draw.text((text_x, text_y), cell, font=font, fill=color)

    # 添加标题
    title = f"#{role_name}词条权重表"
    draw.text((start_x, 20), title, font=waves_font_36, fill=SPECIAL_GOLD)

    # 添加其他
    text = "词条得分：词条数值 * 当前词条权重 / 声骸未对齐最高分 * 对齐分数(50)"
    draw.text((start_x, 750), text, font=waves_font_24, fill="white")
    s = calc_temp["total_grade"]
    text = f"声骸评分标准：SSS≥{s[-1] * 250:.2f}分/ SS≥{s[-2] * 250:.2f}分／S≥{s[-3] * 250:.2f}分 / A≥{s[-4] * 250:.2f}分 / B≥{s[-5] * 250:.2f}分 / C"
    draw.text((start_x, 800), text, font=waves_font_24, fill="white")
    text = "当前角色评分标准仅供参考与娱乐，不代表任何官方或权威的评价。"
    draw.text((start_x, 850), text, font=waves_font_24, fill="white")


async def draw_pic_with_ring(ev: Event, is_force_avatar=False, force_resource_id=None):
    if force_resource_id:
        pic = await get_square_avatar(force_resource_id)
    elif not is_force_avatar:
        pic = await get_event_avatar(ev)
    else:
        pic = await get_qq_avatar(ev.user_id)

    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    img = Image.new("RGBA", (180, 180))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    img.paste(resize_pic, (20, 20), mask)

    return img


async def draw_char_with_ring(char_id):
    pic = await get_square_avatar(char_id)

    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    img = Image.new("RGBA", (180, 180))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    img.paste(resize_pic, (20, 20), mask)

    return img


def get_weapon_icon_bg(star: int = 3) -> Image.Image:
    if star < 3:
        star = 3
    bg_path = TEXT_PATH / f"weapon_icon_bg_{star}.png"
    bg_img = Image.open(bg_path)
    return bg_img


async def generate_online_role_detail(char_id: str):
    char_model = get_char_model(char_id)
    if not char_model:
        return

    weapon_id = DEAFAULT_WEAPON_ID.get(char_model.weaponTypeId)
    if not weapon_id:
        return

    weapon_model = get_weapon_model(weapon_id)
    if not weapon_model:
        return

    char_template_data = copy.deepcopy(await get_template_data())

    # 命座
    for i, j in zip(char_model.chains.values(), char_template_data["chainList"]):
        j["name"] = i.name
        j["description"] = i.desc.format(*i.param)
        j["iconUrl"] = ""
        j["unlocked"] = False

    # 技能
    skill_map = {
        "常态攻击": "1",
        "共鸣技能": "2",
        "共鸣回路": "7",
        "共鸣解放": "3",
        "变奏技能": "6",
        "延奏技能": "8",
    }
    for i in char_template_data["skillList"]:
        temp_skill = i["skill"]
        skill_type = temp_skill["type"]
        skill_detail = char_model.skillTree[skill_map[skill_type]]["skill"]

        temp_skill["name"] = skill_detail.name
        temp_skill["description"] = skill_detail.desc.format(*skill_detail.param)
        temp_skill["iconUrl"] = ""

    # role
    temp_role = char_template_data["role"]
    temp_role["roleName"] = char_model.name
    temp_role["iconUrl"] = ""
    temp_role["roleId"] = char_id
    temp_role["starLevel"] = char_model.starLevel
    temp_role["weaponTypeId"] = char_model.weaponTypeId
    temp_role["weaponTypeName"] = WEAPON_TYPE_ID_MAP[char_model.weaponTypeId]
    temp_role["attributeId"] = char_model.attributeId
    temp_role["attributeName"] = ATTRIBUTE_ID_MAP[char_model.attributeId]

    # 武器
    char_template_data["weaponData"]["resonLevel"] = 1
    temp_weapon = char_template_data["weaponData"]["weapon"]
    temp_weapon["weaponEffectName"] = weapon_model.effect.format(
        *[i[-1] for i in weapon_model.param]
    )
    temp_weapon["weaponIcon"] = ""
    temp_weapon["weaponId"] = weapon_id
    temp_weapon["weaponName"] = weapon_model.name
    temp_weapon["weaponStarLevel"] = weapon_model.starLevel
    temp_weapon["weaponType"] = weapon_model.type

    # 声骸
    char_template_data["phantomData"] = {"cost": 0, "equipPhantomList": None}

    return RoleDetailData.model_validate(char_template_data)


async def get_card_bg(
    w: int,
    h: int,
    bg: str = "bg",
):
    img: Optional[Image.Image] = None
    if ShowConfig.get_config("CardBg").data:
        bg_path = Path(ShowConfig.get_config("CardBgPath").data)
        if bg_path.exists():
            img = Image.open(bg_path).convert("RGBA")
            img = crop_center_img(img, w, h)

    if not img:
        img = get_waves_bg(w, h, bg)

    img = await get_custom_gaussian_blur(img)
    return img
