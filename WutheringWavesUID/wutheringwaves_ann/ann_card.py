import time
from datetime import datetime
from typing import List, Union

from PIL import Image, ImageDraw, ImageOps

from gsuid_core.logger import logger
from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import (
    draw_text_by_line,
    easy_alpha_composite,
    easy_paste,
)

from ..utils.fonts.waves_fonts import (
    ww_font_18,
    ww_font_20,
    ww_font_24,
    ww_font_26,
)
from ..utils.image import add_footer, pic_download_from_url
from ..utils.resource.RESOURCE_PATH import ANN_CARD_PATH
from ..utils.waves_api import waves_api
from ..wutheringwaves_config import PREFIX


async def ann_list_card() -> bytes:
    ann_list = await waves_api.get_ann_list()
    if not ann_list:
        raise Exception("获取游戏公告失败,请检查接口是否正常")

    # 分组并排序
    grouped = {}
    for item in ann_list:
        t = item["eventType"]
        grouped.setdefault(t, []).append(item)

    for data in grouped.values():
        data.sort(key=lambda x: x.get("publishTime", 0), reverse=True)

    # 配置
    W, H_ITEM, H_SECTION, H_HEADER, H_FOOTER = 750, 100, 60, 80, 30
    CONFIGS = {1: ("活动", "#ff6b6b"), 2: ("资讯", "#45b7d1"), 3: ("公告", "#4ecdc4")}

    # 计算高度
    total_items = sum(len(items) for items in grouped.values())
    h = (
        H_HEADER
        + 50
        + len(grouped) * (H_SECTION + 30)
        + total_items * H_ITEM
        + H_FOOTER
    )

    bg = Image.new("RGBA", (W, h), "#f8f9fa")

    # 头部
    header = Image.new("RGBA", (W, H_HEADER), "#4a90e2")
    draw = ImageDraw.Draw(header)
    title = "库街区公告"
    tw = draw.textbbox((0, 0), title, ww_font_26)[2]
    draw.text(((W - tw) // 2, 25), title, "#ffffff", ww_font_26)
    bg = easy_alpha_composite(bg, header, (0, 0))

    # 提示
    tip = f"查看详细内容，使用 {PREFIX}公告#ID 查看详情"
    draw_text_by_line(bg, (30, H_HEADER + 10), tip, ww_font_18, "#8e8e93", W - 60)

    y = H_HEADER + 50

    # 各分类
    for t in [1, 2, 3]:
        if t not in grouped:
            continue

        name, color = CONFIGS[t]
        data = grouped[t]

        # 分类头
        section = Image.new("RGBA", (W - 40, H_SECTION), "#ffffff")
        title_bg = Image.new("RGBA", (W - 40, 40), color)
        title_draw = ImageDraw.Draw(title_bg)
        tw = title_draw.textbbox((0, 0), name, ww_font_24)[2]
        title_draw.text(((W - 40 - tw) // 2, 8), name, "#ffffff", ww_font_24)

        mask = Image.new("L", (W - 40, 40), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 40, 40], 12, 255)
        title_bg.putalpha(mask)
        easy_paste(section, title_bg, (0, 10))

        bg = easy_alpha_composite(bg, section, (20, y))
        y += H_SECTION

        # 条目
        for i, item in enumerate(data):
            card = await create_item_card(W, H_ITEM, item, color, i < len(data) - 1)
            easy_paste(bg, card, (20, y))
            y += H_ITEM
        y += 30

    return await convert_img(add_footer(bg, 600, 20, color="black"))


async def create_item_card(w, h, info, color, sep):
    """创建卡片"""
    bg = Image.new("RGBA", (w - 40, h), "#ffffff")
    draw = ImageDraw.Draw(bg)

    # ID标签
    id_str = str(info.get("id", ""))
    tw = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), id_str, ww_font_18)[
        2
    ]
    id_w = int(tw + 16)
    id_bg = Image.new("RGBA", (id_w, 24), color)
    mask = Image.new("L", (id_w, 24), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, id_w, 24], 12, 255)
    id_bg.putalpha(mask)
    ImageDraw.Draw(id_bg).text(
        (id_w / 2, 12), id_str, "#ffffff", ww_font_18, anchor="mm"
    )
    easy_paste(bg, id_bg, (15, 15))

    # 标题
    title = info.get("postTitle", "未知公告")
    title_x = 25 + id_w
    max_w = w - title_x - 200
    lines = wrap_text_smart(title, ww_font_20, max_w)

    for i, line in enumerate(lines[:2]):
        if i == 1 and len(lines) > 2:
            line = line[:-3] + "..."
        draw_text_by_line(
            bg, (title_x, 18 + i * 24), line, ww_font_20, "#1c1c1e", max_w
        )

    # 日期
    date = format_date(info.get("publishTime", 0))
    draw_text_by_line(bg, (title_x, 75), date, ww_font_18, "#8e8e93", 100)

    # 图片
    await add_preview_image(bg, w, info, color)

    # 边框和分隔线
    if sep:
        draw.line([(20, h - 1), (w - 60, h - 1)], "#f0f0f0", 1)
    draw.rectangle([0, 0, w - 41, h - 1], outline="#e5e5ea", width=1)

    return bg


def format_date(ts):
    """格式化日期"""
    if ts:
        try:
            return datetime.fromtimestamp(ts / 1000).strftime("%m-%d")
        except Exception:
            pass
    return "未知"


async def add_preview_image(bg, w, info, color):
    """添加预览图"""
    url = info.get("coverUrl", "")
    if not url:
        return

    try:
        img = await pic_download_from_url(ANN_CARD_PATH, url)
        if img:
            img = img.resize((100, 70), Image.Resampling.LANCZOS)
            mask = Image.new("L", (100, 70), 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, 100, 70], 8, 255)
            img.putalpha(mask)
            easy_paste(bg, img, (w - 160, 15))
    except Exception as e:
        logger.debug(f"图片加载失败: {e}")


def wrap_text_smart(text, font, max_w):
    """文字换行"""
    if not text:
        return [""]

    draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    lines, line = [], ""

    for char in text:
        test = line + char
        if draw.textbbox((0, 0), test, font)[2] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
                line = char
            else:
                lines.append(char)
                line = ""

    if line:
        lines.append(line)
    return lines or [""]


async def ann_batch_card(post_content: List, drow_height: float) -> bytes:
    im = Image.new("RGB", (1080, drow_height), "#f9f6f2")  # type: ignore
    draw = ImageDraw.Draw(im)
    x, y = 0, 0

    for temp in post_content:
        if temp["contentType"] == 1:
            content = temp["content"]
            drow_duanluo, _, drow_line_height, _ = split_text(content)
            for duanluo, line_count in drow_duanluo:
                draw.text((x, y), duanluo, fill=(0, 0, 0), font=ww_font_26)
                y += drow_line_height * line_count + 30
        elif (
            temp["contentType"] == 2
            and "url" in temp
            and temp["url"].endswith(("jpg", "png", "jpeg", "webp"))
        ):
            img = await pic_download_from_url(ANN_CARD_PATH, temp["url"])
            img_x = 0
            if img.width > im.width:
                ratio = im.width / img.width
                img = img.resize((int(img.width * ratio), int(img.height * ratio)))
            else:
                img_x = (im.width - img.width) // 2
            easy_paste(im, img, (img_x, y))
            y += img.size[1] + 40

    if hasattr(ww_font_26, "getbbox"):
        bbox = ww_font_26.getbbox("囗")
        padding = (
            int(bbox[2] - bbox[0]),
            int(bbox[3] - bbox[1]),
            int(bbox[2] - bbox[0]),
            int(bbox[3] - bbox[1]),
        )
    else:
        w, h = ww_font_26.getsize("囗")  # type: ignore
        padding = (w, h, w, h)
    return await convert_img(ImageOps.expand(im, padding, "#f9f6f2"))


async def ann_detail_card(
    ann_id: int, is_check_time=False
) -> Union[bytes, str, List[bytes]]:
    ann_list = await waves_api.get_ann_list(True)
    if not ann_list:
        raise Exception("获取游戏公告失败,请检查接口是否正常")
    content = [x for x in ann_list if x["id"] == ann_id]
    if not content:
        return "未找到该公告"

    postId = content[0]["postId"]
    res = await waves_api.get_ann_detail(postId)
    if not res:
        return "未找到该公告"

    if is_check_time:
        post_time = format_post_time(res["postTime"])
        now_time = int(time.time())
        logger.debug(
            f"公告id: {ann_id}, post_time: {post_time}, now_time: {now_time}, delta: {now_time-post_time}"
        )
        if post_time < now_time - 86400:
            return "该公告已过期"

    post_content = res["postContent"]
    content_type2_first = [x for x in post_content if x["contentType"] == 2]
    if not content_type2_first and "coverImages" in res:
        _node = res["coverImages"][0]
        _node["contentType"] = 2
        post_content.insert(0, _node)

    if not post_content:
        return "未找到该公告"

    drow_height = 0
    index_start = 0
    index_end = 0
    imgs = []
    for index, temp in enumerate(post_content):
        content_type = temp["contentType"]
        if content_type == 1:
            # 文案
            content = temp["content"]
            (
                x_drow_duanluo,
                x_drow_note_height,
                x_drow_line_height,
                x_drow_height,
            ) = split_text(content)
            drow_height += x_drow_height + 30
        elif (
            content_type == 2
            and "url" in temp
            and temp["url"].endswith(("jpg", "png", "jpeg", "webp"))
        ):
            # 图片
            _size = (temp["imgWidth"], temp["imgHeight"])
            img = await pic_download_from_url(ANN_CARD_PATH, temp["url"])
            img_height = img.size[1]
            if img.width > 1080:
                ratio = 1080 / img.width
                img_height = int(img.height * ratio)
            drow_height += img_height + 40

        index_end = index + 1
        if drow_height > 5000:
            img = await ann_batch_card(post_content[index_start:index_end], drow_height)
            index_start = index_end
            index_end = index + 1
            drow_height = 0
            imgs.append(img)

    if index_start == 0:
        return await ann_batch_card(post_content[index_start:], drow_height)
    else:
        return imgs


def split_text(content: str):
    # 按规定宽度分组
    max_line_height, total_lines = 0, 0
    allText = []
    for text in content.split("\n"):
        duanluo, line_height, line_count = get_duanluo(text)
        max_line_height = max(line_height, max_line_height)
        total_lines += line_count
        allText.append((duanluo, line_count))
    line_height = max_line_height
    total_height = total_lines * line_height
    drow_height = total_lines * line_height
    return allText, total_height, line_height, drow_height


def get_duanluo(text: str):
    txt = Image.new("RGBA", (600, 800), (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)
    # 所有文字的段落
    duanluo = ""
    max_width = 1050
    # 宽度总和
    sum_width = 0
    # 几行
    line_count = 1
    # 行高
    line_height = 0
    for char in text:
        left, top, right, bottom = draw.textbbox((0, 0), char, ww_font_26)
        width, height = (right - left, bottom - top)
        sum_width += width
        if sum_width > max_width:  # 超过预设宽度就修改段落 以及当前行数
            line_count += 1
            sum_width = 0
            duanluo += "\n"
        duanluo += char
        line_height = max(height, line_height)
    if not duanluo.endswith("\n"):
        duanluo += "\n"
    return duanluo, line_height, line_count


def format_post_time(post_time: str) -> int:
    try:
        timestamp = datetime.strptime(post_time, "%Y-%m-%d %H:%M").timestamp()
        return int(timestamp)
    except ValueError:
        pass

    try:
        timestamp = datetime.strptime(post_time, "%Y-%m-%d %H:%M:%S").timestamp()
        return int(timestamp)
    except ValueError:
        pass

    return 0
