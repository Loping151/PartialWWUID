import os
import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List

import aiofiles
from PIL import Image, ImageDraw
from gsuid_core.models import Event
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils import hint
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import PREFIX
from ..utils.api.model import AccountBaseInfo
from ..utils.error_reply import WAVES_CODE_102
from ..utils.resource.constant import NORMAL_LIST
from ..utils.resource.RESOURCE_PATH import PLAYER_PATH
from ..utils.image import (
    GOLD,
    add_footer,
    get_waves_bg,
    get_event_avatar,
    get_square_avatar,
    get_square_weapon,
    cropped_square_avatar,
)
from ..utils.fonts.waves_fonts import (
    waves_font_18,
    waves_font_20,
    waves_font_23,
    waves_font_24,
    waves_font_25,
    waves_font_30,
    waves_font_32,
    waves_font_40,
)

TEXT_PATH = Path(__file__).parent / "texture2d"
HOMO_TAG = ["非到极致", "运气不好", "平稳保底", "小欧一把", "欧狗在此"]

gacha_type_meta_rename = {
    "角色精准调谐": "角色精准调谐",
    "武器精准调谐": "武器精准调谐",
    "角色调谐（常驻池）": "角色常驻调谐",
    "武器调谐（常驻池）": "武器常驻调谐",
    "新手调谐": "新手调谐",
    "新手自选唤取": "新手自选唤取",
    "新手自选唤取（感恩定向唤取）": "感恩定向唤取",
    "角色新旅唤取": "角色新旅唤取",
    "武器新旅唤取": "武器新旅唤取",
}


def get_num_h(num: int, column: int):
    if num == 0:
        return 0
    row = ((num - 1) // column) + 1
    return row


def get_level_from_list(ast: int, lst: List) -> int:
    if ast == 0:
        return 2

    for num_index, num in enumerate(lst):
        if ast <= num:
            level = 4 - num_index
            break
    else:
        level = 0
    return level


async def draw_card_help():
    android = "\n".join(
        [
            "安卓手机获取链接方式",
            "1.打开游戏抽卡界面",
            "2.关闭网络或打开飞行模式",
            "3.点开换取记录",
            "4.长按左上角区域，全选，复制",
            "\n",
        ]
    )
    ios = "\n".join(
        [
            "苹果手机获取方式",
            "1.使用Stream抓包（详细教程网上搜索）",
            "2.关键字搜索:[game2]的请求",
            "3.点击`请求`",
            "4.点击最下方的`查看JSON`，全选，复制",
            "国服域名：[gmserver-api.aki-game2.com]",
            "国际服域名：[gmserver-api.aki-game2.net]",
            "\n",
        ]
    )
    pc = "\n".join(
        [
            "PC获取方式",
            "1.打开游戏抽卡界面，点开换取记录",
            "2.在鸣潮安装的目录下进入目录：`Wuthering Waves\\Wuthering Waves Game\\Client\\Saved\\Logs`",
            "3.找到文件`Client.log`并用记事本打开",
            "4.搜索关键字：aki-gm-resources.aki-game",
            "5.复制一整行链接",
            "\n",
        ]
    )

    yun = "\n".join(
        [
            "云游戏获取方式",
            "1.复制以下链接到浏览器打开",
            "https://ga.loping151.site",
            "2.登录后,依次点击`刷新记录`,`复制记录`按钮",
        ]
    )

    text = "\n".join(
        [
            "如何导入抽卡记录",
            "",
            f"使用命令【{PREFIX}导入抽卡链接 + 你复制的内容】即可开始进行抽卡分析",
            "",
            "抽卡链接具有有效期，请在有效期内尽快导入",
        ]
    )
    msg = [android, ios, pc, yun, text]
    return msg


async def draw_card(uid: str, ev: Event):
    # 获取数据
    gacha_log_path = PLAYER_PATH / str(uid) / "gacha_logs.json"
    if not gacha_log_path.exists():
        return f"[鸣潮] 你还没有抽卡记录噢!\n 请发送 {PREFIX}导入抽卡链接 后重试!"
    async with aiofiles.open(gacha_log_path, "r", encoding="UTF-8") as f:
        raw_data: Dict = json.loads(await f.read())

    gachalogs = raw_data["data"]
    title_num = len([1 for i in gachalogs.keys() if "新手" not in i])

    total_data = {}
    for gacha_name in gachalogs:
        total_data[gacha_name] = {
            "total": 0,  # 抽卡总数
            "avg": 0,  # 抽卡平均数
            "avg_up": 0,  # up平均数
            "remain": 0,  # 已xx抽未出金
            "time_range": "",
            "all_time": "",
            "r_num": [],  # 包含首位的抽卡数量
            "up_list": [],  # 抽到的UP列表
            "rank_s_list": [],  # 抽到的五星列表
            "short_gacha_data": {"time": 0, "num": 0},
            "long_gacha_data": {"time": 0, "num": 0},
            "level": 0,  # 抽卡等级
        }

    for gacha_name in gachalogs:
        num = 1
        gacha_data = gachalogs[gacha_name]
        current_data = total_data[gacha_name]
        for index, data in enumerate(gacha_data[::-1]):
            if index == 0:
                current_data["time_range"] = data["time"]
            if index == len(gacha_data) - 1:
                time_1 = datetime.strptime(data["time"], "%Y-%m-%d %H:%M:%S")
                time_2 = datetime.strptime(
                    current_data["time_range"], "%Y-%m-%d %H:%M:%S"
                )
                current_data["all_time"] = (time_1 - time_2).total_seconds()

                current_data["time_range"] += "~" + data["time"]

            if data["qualityLevel"] == 5:
                data["gacha_num"] = num

                # 判断是否是UP
                if data["name"] in NORMAL_LIST:
                    data["is_up"] = False
                else:
                    data["is_up"] = True

                current_data["r_num"].append(num)
                current_data["rank_s_list"].append(data)
                if data["is_up"]:
                    current_data["up_list"].append(data)

                num = 1
            else:
                num += 1
            current_data["total"] += 1

        current_data["remain"] = num - 1
        if len(current_data["rank_s_list"]) == 0:
            current_data["avg"] = "-"
        else:
            _d = sum(current_data["r_num"]) / len(current_data["r_num"])
            current_data["avg"] = float("{:.2f}".format(_d))
        # 计算平均up数量
        if len(current_data["up_list"]) == 0:
            current_data["avg_up"] = "-"
        else:
            _u = sum(current_data["r_num"]) / len(current_data["up_list"])
            current_data["avg_up"] = float("{:.2f}".format(_u))

        current_data["level"] = 2
        if current_data["avg_up"] == "-" and current_data["avg"] == "-":
            current_data["level"] = 2
        else:
            if gacha_name == "角色精准调谐":
                if current_data["avg_up"] != "-":
                    current_data["level"] = get_level_from_list(
                        current_data["avg_up"], [74, 87, 99, 105, 120]
                    )
                elif current_data["avg"] != "-":
                    current_data["level"] = get_level_from_list(
                        current_data["avg"], [53, 60, 68, 73, 75]
                    )
            elif gacha_name in [
                "武器精准调谐",
                "角色调谐（常驻池）",
                "武器调谐（常驻池）",
                "新手自选唤取",
            ]:
                if current_data["avg"] != "-":
                    current_data["level"] = get_level_from_list(
                        current_data["avg"], [45, 52, 59, 65, 70]
                    )
            elif gacha_name == "新手调谐":
                if current_data["avg"] != "-":
                    current_data["level"] = get_level_from_list(
                        current_data["avg"], [10, 20, 30, 40, 45]
                    )

    oset = 280
    bset = 170

    _numlen = 0
    newbie_flag = False
    for name in total_data:
        _num = len(total_data[name]["rank_s_list"])
        if "新手" in name:
            if _num > 0:
                newbie_flag = True
        else:
            _num = len(total_data[name]["rank_s_list"])
            if _num == 0:
                _numlen += 50
            else:
                _numlen += bset * get_num_h(_num, 5)

    _newbielen = 395 if newbie_flag else 0
    _header = 380
    footer = 50
    w, h = 1000, _header + title_num * oset + _numlen + _newbielen + footer

    card_img = get_waves_bg(w, h)
    card_draw = ImageDraw.Draw(card_img)

    item_fg = Image.open(TEXT_PATH / "char_bg.png")
    up_icon = Image.open(TEXT_PATH / "up_tag.png")
    up_icon = up_icon.resize((68, 52))

    async def draw_pic(item) -> Image.Image:
        item_bg = Image.new("RGBA", (167, 170))
        item_fg_cp = item_fg.copy()
        item_bg.paste(item_fg_cp, (0, 0), item_fg_cp)

        item_temp = Image.new("RGBA", (167, 170))
        if item["resourceType"] == "武器":
            item_icon = await get_square_weapon(item["resourceId"])
            item_icon = item_icon.resize((130, 130)).convert("RGBA")
            item_temp.paste(item_icon, (22, 0), item_icon)
        else:
            item_icon = await get_square_avatar(item["resourceId"])
            item_icon = await cropped_square_avatar(item_icon, 130)
            item_temp.paste(item_icon, (22, 0), item_icon)

        item_bg.paste(item_temp, (-2, -2), item_temp)
        gnum = item["gacha_num"]
        if gnum >= 70:
            # gcolor = (223, 88, 75)
            gcolor = (230, 58, 58)
        elif gnum <= 40:
            gcolor = (43, 210, 43)
        else:
            gcolor = "white"
        info_block = Image.new("RGBA", (137, 28), color=(255, 255, 255, 0))
        info_block_draw = ImageDraw.Draw(info_block)
        info_block_draw.rectangle([0, 0, 137, 28], fill=(0, 0, 0, int(0.6 * 255)))
        info_block_draw.text(
            (65, 12), f"{item['gacha_num']}抽", gcolor, waves_font_20, "mm"
        )

        item_bg.paste(info_block, (15, 130), info_block)

        if item["is_up"]:
            up_icon_cp = up_icon.copy()
            item_bg.paste(up_icon_cp, (88, 3), up_icon_cp)
        return item_bg

    y = 0
    gindex = 0
    for _, gacha_name in enumerate(total_data):
        if "新手" in gacha_name:
            continue
        gacha_data = total_data[gacha_name]
        title = Image.open(TEXT_PATH / "bar.png")
        title_draw = ImageDraw.Draw(title)

        remain_s = f"{gacha_data['remain']}"
        avg_s = f"{gacha_data['avg']}"
        avg_up_s = f"{gacha_data['avg_up']}"
        total = f"{gacha_data['total']}"
        level = gacha_data["level"]

        if gacha_data["time_range"]:
            time_range = gacha_data["time_range"]
        else:
            time_range = "暂未抽过卡!"
        title_draw.text(
            (110, 120),
            time_range,
            (220, 220, 220),
            waves_font_18,
            "lm",
        )

        level_path = TEXT_PATH / f"{level}"
        level_icon = Image.open(random.choice(list(level_path.iterdir())))
        level_icon = level_icon.resize((140, 140)).convert("RGBA")
        tag = HOMO_TAG[level]

        title_draw.text((160, 178), avg_s, "white", waves_font_32, "mm")
        title_draw.text((300, 178), avg_up_s, "white", waves_font_32, "mm")
        title_draw.text((457, 178), total, "white", waves_font_32, "mm")
        title_draw.text(
            (110, 80), gacha_type_meta_rename[gacha_name], "white", waves_font_40, "lm"
        )
        title_draw.text((380, 87), "已", "white", waves_font_23, "rm")
        title_draw.text((410, 84), remain_s, "red", waves_font_40, "mm")
        title_draw.text((530, 87), "抽未出金", "white", waves_font_23, "rm")

        title.paste(level_icon, (710, 51), level_icon)
        title_draw.text((783, 225), tag, "white", waves_font_24, "mm")

        card_img.paste(title, (10, _header + y + gindex * oset), title)
        gindex += 1
        s_list = gacha_data["rank_s_list"]
        s_list.reverse()
        for index, item in enumerate(s_list):
            item_bg = await draw_pic(item)

            _x = 95 + 162 * (index % 5)
            _y = _header + bset * (index // 5) + y + gindex * oset

            card_img.paste(
                item_bg,
                (_x, _y),
                item_bg,
            )
        if not s_list:
            card_draw.text(
                (475, _header + y + gindex * oset + 25),
                "当前该卡池暂未有5星数据噢!",
                (157, 157, 157),
                waves_font_20,
                "mm",
            )
            y += 50
        else:
            y += get_num_h(len(s_list), 5) * bset

    newbie_bg = Image.open(TEXT_PATH / "newbie.png")
    nindex = 0
    for _, gacha_name in enumerate(total_data):
        if "新手" not in gacha_name:
            continue
        gacha_data = total_data[gacha_name]

        s_list = gacha_data["rank_s_list"]
        if not s_list:
            continue
        item_bg = await draw_pic(s_list[0])

        newbie_bg_cp = newbie_bg.copy()
        newbie_bg_cp_draw = ImageDraw.Draw(newbie_bg_cp)
        newbie_bg_cp.paste(item_bg, (115, 220), item_bg)
        newbie_bg_cp_draw.text(
            (200, 160), gacha_type_meta_rename[gacha_name], "white", waves_font_40, "mm"
        )
        if gacha_data["time_range"]:
            time_range = (
                gacha_data["time_range"].split("~")[1]
                if "~" in gacha_data["time_range"]
                else gacha_data["time_range"]
            )
        else:
            time_range = "暂未抽过卡!"
        newbie_bg_cp_draw.text(
            (100, 200),
            time_range,
            "white",
            waves_font_18,
            "lm",
        )

        card_img.paste(
            newbie_bg_cp,
            (10 + nindex * 290, _header + y + gindex * oset - 80),
            newbie_bg_cp,
        )
        nindex += 1

    await draw_uid_avatar(uid, ev, card_img)

    card_img = add_footer(card_img, 600, 20)
    card_img = await convert_img(card_img)
    return card_img


async def draw_pic_with_ring(ev: Event):
    pic = await get_event_avatar(ev, is_valid_at_param=False)

    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    img = Image.new("RGBA", (320, 320))
    mask = mask_pic.resize((250, 250))
    resize_pic = crop_center_img(pic, 250, 250)
    img.paste(resize_pic, (20, 20), mask)
    return img


async def get_random_card_polygon(ev: Event):
    CARD_POLYGON_PATH = TEXT_PATH / "card_polygon"
    path = random.choice(os.listdir(f"{CARD_POLYGON_PATH}"))
    card_img = Image.open(f"{CARD_POLYGON_PATH}/{path}").convert("RGBA")

    avatar = await draw_pic_with_ring(ev)
    avatar = avatar.resize((500, 500))
    card_img.paste(avatar, (-10, 150), avatar)

    avatar_ring = Image.open(TEXT_PATH / "avatar_ring.png")
    avatar_ring = avatar_ring.resize((450, 450))
    card_img.paste(avatar_ring, (-10, 150), avatar_ring)

    return card_img.resize((280, 400))


async def draw_uid_avatar(uid, ev, card_img):
    if waves_api.is_net(uid):
        title = Image.open(TEXT_PATH / "title.png")
        base_info_draw = ImageDraw.Draw(title)
        base_info_draw.text((346, 370), f"特征码:  {uid}", GOLD, waves_font_25, "lm")

        avatar = await draw_pic_with_ring(ev)
        avatar_ring = Image.open(TEXT_PATH / "avatar_ring.png")

        card_img.paste(avatar, (346, 40), avatar)
        avatar_ring = avatar_ring.resize((300, 300))
        card_img.paste(avatar_ring, (340, 35), avatar_ring)

        card_img.paste(title, (0, 0), title)

    else:
        _, ck = await waves_api.get_ck_result(uid, ev.user_id, ev.bot_id)
        if not ck:
            return hint.error_reply(WAVES_CODE_102)
        account_info = await waves_api.get_base_info(uid, ck)
        if not account_info.success:
            return account_info.throw_msg()
        account_info = AccountBaseInfo.model_validate(account_info.data)

        base_info_bg = Image.open(TEXT_PATH / "base_info_bg.png")
        base_info_draw = ImageDraw.Draw(base_info_bg)
        base_info_draw.text(
            (275, 120), f"{account_info.name[:7]}", "white", waves_font_30, "lm"
        )
        base_info_draw.text(
            (226, 173), f"特征码:  {account_info.id}", GOLD, waves_font_25, "lm"
        )
        base_info_bg = base_info_bg.resize((900, 450))
        card_img.alpha_composite(base_info_bg, (110, 30))
        #
        card_polygon = await get_random_card_polygon(ev)
        card_img.alpha_composite(card_polygon, (80, 0))
