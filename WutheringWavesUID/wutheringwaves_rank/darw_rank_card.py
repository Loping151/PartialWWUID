import asyncio
import time
from pathlib import Path
from typing import List, Optional, Union

from PIL import Image, ImageDraw
from pydantic import BaseModel

from gsuid_core.bot import Bot
from gsuid_core.logger import logger
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.api.model import RoleDetailData, WeaponData
from ..utils.cache import TimedCache
from ..utils.calc import WuWaCalc
from ..utils.calculate import (
    calc_phantom_score,
    get_calc_map,
    get_total_score_bg,
)
from ..utils.char_info_utils import get_all_role_detail_info_list
from ..utils.damage.abstract import DamageRankRegister
from ..utils.database.models import WavesBind, WavesUser
from ..utils.fonts.waves_fonts import (
    waves_font_14,
    waves_font_16,
    waves_font_18,
    waves_font_20,
    waves_font_24,
    waves_font_30,
    waves_font_34,
    waves_font_40,
    waves_font_44,
)
from ..utils.image import (
    CHAIN_COLOR,
    GREY,
    RED,
    SPECIAL_GOLD,
    WEAPON_RESONLEVEL_COLOR,
    add_footer,
    get_attribute,
    get_attribute_effect,
    get_qq_avatar,
    get_role_pile_old,
    get_square_avatar,
    get_square_weapon,
    get_waves_bg,
)
from ..utils.name_convert import alias_to_char_name, char_name_to_char_id
from ..utils.resource.constant import SPECIAL_CHAR, SPECIAL_CHAR_NAME
from ..utils.util import hide_uid
from ..wutheringwaves_config import PREFIX, WutheringWavesConfig

rank_length = 20  # 排行长度
TEXT_PATH = Path(__file__).parent / "texture2d"
TITLE_I = Image.open(TEXT_PATH / "title.png")
TITLE_II = Image.open(TEXT_PATH / "title2.png")
avatar_mask = Image.open(TEXT_PATH / "avatar_mask.png")
weapon_icon_bg_3 = Image.open(TEXT_PATH / "weapon_icon_bg_3.png")
weapon_icon_bg_4 = Image.open(TEXT_PATH / "weapon_icon_bg_4.png")
weapon_icon_bg_5 = Image.open(TEXT_PATH / "weapon_icon_bg_5.png")
promote_icon = Image.open(TEXT_PATH / "promote_icon.png")
char_mask = Image.open(TEXT_PATH / "char_mask.png")
logo_img = Image.open(TEXT_PATH / "logo_small_2.png")
pic_cache = TimedCache(86400, 200)


class RankInfo(BaseModel):
    roleDetail: RoleDetailData  # 角色明细
    qid: str  # qq id
    uid: str  # uid
    level: int  # 角色等级
    chain: int  # 命座
    chainName: str  # 命座
    score: float  # 角色评分
    score_bg: str  # 评分背景
    expected_damage: str  # 期望伤害
    expected_damage_int: int  # 期望伤害
    sonata_name: str  # 合鸣效果


async def get_one_rank_info(user_id, uid, role_detail, rankDetail):
    equipPhantomList = role_detail.phantomData.equipPhantomList

    calc: WuWaCalc = WuWaCalc(role_detail)
    calc.phantom_pre = calc.prepare_phantom()
    calc.phantom_card = calc.enhance_summation_phantom_value(calc.phantom_pre)
    calc.calc_temp = get_calc_map(
        calc.phantom_card,
        role_detail.role.roleName,
        role_detail.role.roleId,
    )

    # 评分
    phantom_score = 0
    # calc_temp = get_calc_map(phantom_sum_value, role_detail.role.roleName)
    for i, _phantom in enumerate(equipPhantomList):
        if _phantom and _phantom.phantomProp:
            props = _phantom.get_props()
            _score, _bg = calc_phantom_score(
                role_detail.role.roleId, props, _phantom.cost, calc.calc_temp
            )
            phantom_score += _score

    if phantom_score == 0:
        return

    phantom_score = round(phantom_score, 2)
    phantom_bg = get_total_score_bg(
        role_detail.role.roleName, phantom_score, calc.calc_temp
    )

    calc.role_card = calc.enhance_summation_card_value(calc.phantom_card)
    calc.damageAttribute = calc.card_sort_map_to_attribute(calc.role_card)

    if rankDetail:
        crit_damage, expected_damage = rankDetail["func"](
            calc.damageAttribute, role_detail
        )
    else:
        expected_damage = "0"

    sonata_name = ""
    ph_detail = calc.phantom_card.get("ph_detail", [])
    if isinstance(ph_detail, list):
        for ph in ph_detail:
            if ph.get("ph_num") == 5:
                sonata_name = ph.get("ph_name", "")
                break

            if ph.get("isFull"):
                sonata_name = ph.get("ph_name", "")
                break

    rankInfo = RankInfo(
        **{
            "roleDetail": role_detail,
            "qid": user_id,
            "uid": uid,
            "level": role_detail.role.level,
            "chain": role_detail.get_chain_num(),
            "chainName": role_detail.get_chain_name(),
            "score": round(int(phantom_score * 100) / 100, ndigits=2),
            "score_bg": phantom_bg,
            "expected_damage": expected_damage,
            "expected_damage_int": int(expected_damage.replace(",", "")),
            "sonata_name": sonata_name,
        }
    )
    return rankInfo


async def find_role_detail(
    uid: str, char_id: Union[int, str, List[str], List[int]]
) -> Optional[RoleDetailData]:
    role_details = await get_all_role_detail_info_list(uid)
    if role_details is None:
        return None

    # 将char_id转换为字符串列表进行匹配
    if isinstance(char_id, (int, str)):
        char_id_list = [str(char_id)]
    else:
        char_id_list = [str(cid) for cid in char_id]

    # 使用生成器来进行过滤
    return next(
        (role for role in role_details if str(role.role.roleId) in char_id_list), None
    )


async def get_rank_info_for_user(
    user: WavesBind,
    char_id,
    find_char_id,
    rankDetail,
    tokenLimitFlag,
    wavesTokenUsersMap,
):
    rankInfoList = []
    if not user.uid:
        return rankInfoList

    tasks = [find_role_detail(uid, find_char_id) for uid in user.uid.split("_")]
    role_details = await asyncio.gather(*tasks)

    for uid, role_detail in zip(user.uid.split("_"), role_details):
        if (
            tokenLimitFlag
            and (
                user.user_id,
                uid,
            )
            not in wavesTokenUsersMap
        ):
            continue
        if not role_detail:
            continue
        if not role_detail.phantomData or not role_detail.phantomData.equipPhantomList:
            continue

        rankInfo = await get_one_rank_info(user.user_id, uid, role_detail, rankDetail)
        if not rankInfo:
            continue
        rankInfoList.append(rankInfo)

    return rankInfoList


async def get_all_rank_info(
    users: List[WavesBind],
    char_id,
    find_char_id,
    rankDetail,
    tokenLimitFlag,
    wavesTokenUsersMap,
):
    semaphore = asyncio.Semaphore(50)

    async def process_user(user):
        async with semaphore:
            return await get_rank_info_for_user(
                user,
                char_id,
                find_char_id,
                rankDetail,
                tokenLimitFlag,
                wavesTokenUsersMap,
            )

    tasks = [process_user(user) for user in users]
    results = await asyncio.gather(*tasks)

    # Flatten the results list
    rankInfoList = [rank_info for result in results for rank_info in result]
    return rankInfoList


async def get_waves_token_condition(ev):
    wavesTokenUsersMap = {}
    flag = False

    # 群组 不限制token
    WavesRankUseTokenGroup = WutheringWavesConfig.get_config(
        "WavesRankNoLimitGroup"
    ).data
    if WavesRankUseTokenGroup and ev.group_id in WavesRankUseTokenGroup:
        return flag, wavesTokenUsersMap

    # 群组 自定义的
    WavesRankUseTokenGroup = WutheringWavesConfig.get_config(
        "WavesRankUseTokenGroup"
    ).data
    # 全局 主人定义的
    RankUseToken = WutheringWavesConfig.get_config("RankUseToken").data
    if (
        WavesRankUseTokenGroup and ev.group_id in WavesRankUseTokenGroup
    ) or RankUseToken:
        wavesTokenUsers = await WavesUser.get_waves_all_user()
        wavesTokenUsersMap = {(w.user_id, w.uid): w.cookie for w in wavesTokenUsers}
        flag = True

    return flag, wavesTokenUsersMap


async def draw_rank_img(
    bot: Bot, ev: Event, char: str, rank_type: str
) -> Union[str, bytes]:
    char_id = char_name_to_char_id(char)
    if not char_id:
        return (
            f"[鸣潮] 角色名【{char}】无法找到, 可能暂未适配, 请先检查输入是否正确！\n"
        )
    char_name = alias_to_char_name(char)

    rankDetail = DamageRankRegister.find_class(char_id)
    if not rankDetail and rank_type == "伤害":
        return f"[鸣潮] 角色【{char_name}排行】暂未适配伤害计算，请等待作者更新！\n"

    if char_id in SPECIAL_CHAR:
        find_char_id = SPECIAL_CHAR[char_id]
    else:
        find_char_id = char_id

    start_time = time.time()
    logger.info(f"[get_rank_info_for_user] start: {start_time}")
    # 获取群里的所有拥有该角色人的数据
    users = await WavesBind.get_group_all_uid(ev.group_id)

    tokenLimitFlag, wavesTokenUsersMap = await get_waves_token_condition(ev)
    if not users:
        msg = []
        msg.append(f"[鸣潮] 群【{ev.group_id}】暂无【{char}】面板")
        msg.append(f"请使用【{PREFIX}刷新面板】后再使用此功能！")
        if tokenLimitFlag:
            msg.append(
                f"当前排行开启了登录验证，请使用命令【{PREFIX}登录】登录后此功能！"
            )
        msg.append("")
        return "\n".join(msg)

    self_uid = None
    role_detail = None
    try:
        self_uid = await WavesBind.get_uid_by_game(ev.user_id, ev.bot_id)
        if self_uid:
            role_detail = await find_role_detail(self_uid, find_char_id)
            if role_detail:
                char_id = str(role_detail.role.roleId)
    except Exception as _:
        pass

    damage_title = (rankDetail and rankDetail["title"]) or "无"
    rankInfoList = await get_all_rank_info(
        list(users),
        char_id,
        find_char_id,
        rankDetail,
        tokenLimitFlag,
        wavesTokenUsersMap,
    )
    if len(rankInfoList) == 0:
        msg = []
        msg.append(f"[鸣潮] 群【{ev.group_id}】暂无【{char}】面板")
        msg.append(f"请使用【{PREFIX}刷新面板】后再使用此功能！")
        if tokenLimitFlag:
            msg.append(
                f"当前排行开启了登录验证，请使用命令【{PREFIX}登录】登录后此功能！"
            )
        msg.append("")
        return "\n".join(msg)

    if rank_type == "评分":
        rankInfoList.sort(
            key=lambda i: (i.score, i.expected_damage_int, i.level, i.chain),
            reverse=True,
        )
    else:
        rankInfoList.sort(
            key=lambda i: (i.expected_damage_int, i.score, i.level, i.chain),
            reverse=True,
        )

    rankId = None
    rankInfo = None

    if not rankId:
        rankId, rankInfo = next(
            (
                (rankId, rankInfo)
                for rankId, rankInfo in enumerate(rankInfoList, start=1)
                if rankInfo.uid == self_uid and ev.user_id == rankInfo.qid
            ),
            (None, None),
        )

    rankInfoList = rankInfoList[:rank_length]
    if rankId and rankInfo and rankId > rank_length:
        rankInfoList.append(rankInfo)

    totalNum = len(rankInfoList)
    title_h = 500
    bar_star_h = 110
    h = title_h + totalNum * bar_star_h + 80
    card_img = get_waves_bg(1050, h, "bg3")
    card_img_draw = ImageDraw.Draw(card_img)

    bar = Image.open(TEXT_PATH / "bar.png")
    total_score = 0
    total_damage = 0

    tasks = [
        get_avatar(ev, rank.qid, rank.roleDetail.role.roleId) for rank in rankInfoList
    ]
    results = await asyncio.gather(*tasks)

    for index, temp in enumerate(zip(rankInfoList, results)):
        rank, role_avatar = temp
        rank: RankInfo
        rank_role_detail: RoleDetailData = rank.roleDetail
        bar_bg = bar.copy()
        bar_star_draw = ImageDraw.Draw(bar_bg)
        # role_avatar = await get_avatar(ev, rank.qid, role_detail.role.roleId)
        bar_bg.paste(role_avatar, (100, 0), role_avatar)

        role_attribute = await get_attribute(
            rank_role_detail.role.attributeName or "导电", is_simple=True
        )
        role_attribute = role_attribute.resize((40, 40)).convert("RGBA")
        bar_bg.alpha_composite(role_attribute, (300, 20))

        # 命座
        info_block = Image.new("RGBA", (46, 20), color=(255, 255, 255, 0))
        info_block_draw = ImageDraw.Draw(info_block)
        fill = CHAIN_COLOR[rank.chain] + (int(0.9 * 255),)
        info_block_draw.rounded_rectangle([0, 0, 46, 20], radius=6, fill=fill)
        info_block_draw.text((5, 10), f"{rank.chainName}", "white", waves_font_18, "lm")
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
        if rank.score > 0.0:
            score_bg = Image.open(TEXT_PATH / f"score_{rank.score_bg}.png")
            bar_bg.alpha_composite(score_bg, (320, 2))
            bar_star_draw.text(
                (466, 42),
                f"{int(rank.score * 100) / 100:.2f}",
                "white",
                waves_font_30,
                "mm",
            )
            bar_star_draw.text((466, 75), "声骸分数", SPECIAL_GOLD, waves_font_16, "mm")

        # 合鸣效果
        if rank.sonata_name:
            effect_image = await get_attribute_effect(rank.sonata_name)
            effect_image = effect_image.resize((50, 50))
            bar_bg.alpha_composite(effect_image, (533, 15))
            sonata_name = rank.sonata_name
        else:
            sonata_name = "合鸣效果"

        sonata_font = waves_font_16
        if len(sonata_name) > 4:
            sonata_font = waves_font_14
        bar_star_draw.text((558, 75), f"{sonata_name}", "white", sonata_font, "mm")

        # 武器
        weapon_bg_temp = Image.new("RGBA", (600, 300))

        weaponData: WeaponData = rank_role_detail.weaponData
        weapon_icon = await get_square_weapon(weaponData.weapon.weaponId)
        weapon_icon = crop_center_img(weapon_icon, 110, 110)
        weapon_icon_bg = get_weapon_icon_bg(weaponData.weapon.weaponStarLevel)
        weapon_icon_bg.paste(weapon_icon, (10, 20), weapon_icon)

        weapon_bg_temp_draw = ImageDraw.Draw(weapon_bg_temp)
        weapon_bg_temp_draw.text(
            (200, 30),
            f"{weaponData.weapon.weaponName}",
            SPECIAL_GOLD,
            waves_font_40,
            "lm",
        )
        weapon_bg_temp_draw.text(
            (203, 75), f"Lv.{weaponData.level}/90", "white", waves_font_30, "lm"
        )

        _x = 220
        _y = 120
        wrc_fill = WEAPON_RESONLEVEL_COLOR[weaponData.resonLevel or 0] + (
            int(0.8 * 255),
        )
        weapon_bg_temp_draw.rounded_rectangle(
            [_x - 15, _y - 15, _x + 50, _y + 15], radius=7, fill=wrc_fill
        )
        weapon_bg_temp_draw.text(
            (_x, _y), f"精{weaponData.resonLevel}", "white", waves_font_24, "lm"
        )

        weapon_bg_temp.alpha_composite(weapon_icon_bg, dest=(45, 0))

        bar_bg.alpha_composite(weapon_bg_temp.resize((260, 130)), dest=(580, 25))

        # 伤害
        if damage_title == "无":
            bar_star_draw.text((870, 55), "等待更新(:", GREY, waves_font_34, "mm")
        else:
            bar_star_draw.text(
                (870, 45), f"{rank.expected_damage}", SPECIAL_GOLD, waves_font_34, "mm"
            )
            bar_star_draw.text(
                (870, 75), f"{damage_title}", "white", waves_font_16, "mm"
            )

        # 排名
        rank_color = (54, 54, 54)
        if index == 0:
            rank_color = (255, 0, 0)
        elif index == 1:
            rank_color = (255, 180, 0)
        elif index == 2:
            rank_color = (185, 106, 217)

        def draw_rank_id(rank_id, size=(50, 50), draw=(24, 24), dest=(40, 30)):
            info_rank = Image.new("RGBA", size, color=(255, 255, 255, 0))
            rank_draw = ImageDraw.Draw(info_rank)
            rank_draw.rounded_rectangle(
                [0, 0, size[0], size[1]], radius=8, fill=rank_color + (int(0.9 * 255),)
            )
            rank_draw.text(draw, f"{rank_id}", "white", waves_font_34, "mm")
            bar_bg.alpha_composite(info_rank, dest)

        rank_id = index + 1
        if rankId is not None and rank_id > rank_length:
            rank_id = rankId

        if rank_id is not None and rank_id > 999:
            draw_rank_id("999+", size=(100, 50), draw=(50, 24), dest=(10, 30))
        elif rank_id is not None and rank_id > 99:
            draw_rank_id(rank_id, size=(75, 50), draw=(37, 24), dest=(25, 30))
        else:
            draw_rank_id(rank_id or 0, size=(50, 50), draw=(24, 24), dest=(40, 30))

        # uid
        uid_color = "white"
        if rankId is not None and rankId == rank_id:
            uid_color = RED
        bar_star_draw.text(
            (210, 75), f"{hide_uid(rank.uid)}", uid_color, waves_font_20, "lm"
        )

        # 贴到背景
        card_img.paste(bar_bg, (0, title_h + index * bar_star_h), bar_bg)

        if rank_id is not None and rank_id <= rank_length:
            total_score += rank.score
            total_damage += rank.expected_damage_int

    if rankId is not None and rankId > rank_length:
        totalNum -= 1

    avg_score = f"{total_score / totalNum:.1f}" if totalNum != 0 else "0"
    avg_damage = f"{total_damage / totalNum:,.0f}" if totalNum != 0 else "0"

    title = TITLE_I.copy()
    title_draw = ImageDraw.Draw(title)
    # logo
    title.alpha_composite(logo_img.copy(), dest=(50, 65))

    # 人物bg
    pile = await get_role_pile_old(char_id, custom=True)
    title.paste(pile, (450, -120), pile)
    title_draw.text((200, 335), f"{avg_score}", "white", waves_font_44, "mm")
    title_draw.text((200, 375), "平均声骸分数", SPECIAL_GOLD, waves_font_20, "mm")

    if damage_title != "无":
        title_draw.text((390, 335), f"{avg_damage}", "white", waves_font_44, "mm")
        title_draw.text((390, 375), "平均伤害", SPECIAL_GOLD, waves_font_20, "mm")

    if char_id in SPECIAL_CHAR_NAME:
        char_name = SPECIAL_CHAR_NAME[char_id]

    title_name = f"{char_name}{rank_type}群排行"
    title_draw.text((140, 265), f"{title_name}", "black", waves_font_30, "lm")

    # 备注
    rank_row_title = "入榜条件"
    rank_row = f"1.本群内使用命令【{PREFIX}刷新面板】刷新过面板"
    title_draw.text((20, 420), f"{rank_row_title}", SPECIAL_GOLD, waves_font_16, "lm")
    title_draw.text((90, 420), f"{rank_row}", GREY, waves_font_16, "lm")
    if tokenLimitFlag:
        rank_row = f"2.使用命令【{PREFIX}登录】登录过的用户"
        title_draw.text((90, 438), f"{rank_row}", GREY, waves_font_16, "lm")

    if rank_type == "伤害":
        temp_notes = (
            "排行标准：以期望伤害（计算暴击率的伤害，不代表实际伤害) 为排序的排名"
        )
    else:
        temp_notes = "排行标准：以声骸分数（声骸评分高，不代表实际伤害高) 为排序的排名"
    card_img_draw.text((450, 500), f"{temp_notes}", SPECIAL_GOLD, waves_font_16, "lm")

    img_temp = Image.new("RGBA", char_mask.size)
    img_temp.paste(title, (0, 0), char_mask.copy())
    card_img.alpha_composite(img_temp, (0, 0))
    card_img = add_footer(card_img)
    card_img = await convert_img(card_img)

    logger.info(f"[get_rank_info_for_user] end: {time.time() - start_time}")
    return card_img


async def get_avatar(
    ev: Event,
    qid: Optional[Union[int, str]],
    char_id: Union[int, str],
) -> Image.Image:
    if ev.bot_id == "onebot":
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


def get_weapon_icon_bg(star: int = 3) -> Image.Image:
    if star < 3:
        star = 3

    if star == 3:
        return weapon_icon_bg_3.copy()
    elif star == 4:
        return weapon_icon_bg_4.copy()
    else:
        return weapon_icon_bg_5.copy()
