import textwrap
from pathlib import Path
from typing import Dict, Optional

from PIL import Image, ImageDraw

from gsuid_core.utils.image.convert import convert_img

from ..utils.ascension.char import get_char_model
from ..utils.ascension.model import (
    Chain,
    CharacterModel,
    Skill,
    SkillLevel,
    Stats,
)
from ..utils.fonts.waves_fonts import (
    waves_font_12,
    waves_font_24,
    waves_font_70,
    waves_font_origin,
)
from ..utils.image import (
    GREY,
    SPECIAL_GOLD,
    add_footer,
    get_role_pile,
    get_waves_bg,
)

TEXT_PATH = Path(__file__).parent / "texture2d"


async def draw_char_wiki(char_id: str, query_role_type: str):
    if query_role_type == "天赋":
        return await draw_char_skill(char_id)
    elif query_role_type == "命座":
        return await draw_char_chain(char_id)

    return ""


async def draw_char_skill(char_id: str):
    char_model: Optional[CharacterModel] = get_char_model(char_id)
    if char_model is None:
        return ""

    _, char_pile = await get_role_pile(char_id)

    char_pic = char_pile.resize((600, int(600 / char_pile.size[0] * char_pile.size[1])))

    char_bg = Image.open(TEXT_PATH / "title_bg.png")
    char_bg = char_bg.resize((1000, int(1000 / char_bg.size[0] * char_bg.size[1])))
    char_bg_draw = ImageDraw.Draw(char_bg)
    # 名字
    char_bg_draw.text((580, 120), f"{char_model.name}", "black", waves_font_70, "lm")
    # 稀有度
    rarity_pic = Image.open(TEXT_PATH / f"rarity_{char_model.starLevel}.png")
    rarity_pic = rarity_pic.resize(
        (180, int(180 / rarity_pic.size[0] * rarity_pic.size[1]))
    )

    # 90级别数据
    max_stats: Stats = char_model.get_max_level_stat()
    char_stats = await parse_char_stats(max_stats)

    # 技能
    char_skill = await parse_char_skill(char_model.skillTree)

    card_img = get_waves_bg(1000, char_bg.size[1] + char_skill.size[1] + 50, "bg6")

    char_bg.alpha_composite(char_pic, (0, -100))
    char_bg.alpha_composite(char_stats, (580, 340))
    char_bg.alpha_composite(rarity_pic, (560, 160))
    card_img.paste(char_bg, (0, -5), char_bg)
    card_img.alpha_composite(char_skill, (0, 600))

    card_img = add_footer(card_img, 800, 20, color="hakush")
    card_img = await convert_img(card_img)
    return card_img


async def draw_char_chain(char_id: str):
    char_model: Optional[CharacterModel] = get_char_model(char_id)
    if char_model is None:
        return ""

    _, char_pile = await get_role_pile(char_id)

    char_pic = char_pile.resize((600, int(600 / char_pile.size[0] * char_pile.size[1])))

    char_bg = Image.open(TEXT_PATH / "title_bg.png")
    char_bg = char_bg.resize((1000, int(1000 / char_bg.size[0] * char_bg.size[1])))
    char_bg_draw = ImageDraw.Draw(char_bg)
    # 名字
    char_bg_draw.text((580, 120), f"{char_model.name}", "black", waves_font_70, "lm")
    # 稀有度
    rarity_pic = Image.open(TEXT_PATH / f"rarity_{char_model.starLevel}.png")
    rarity_pic = rarity_pic.resize(
        (180, int(180 / rarity_pic.size[0] * rarity_pic.size[1]))
    )

    # 90级别数据
    max_stats: Stats = char_model.get_max_level_stat()
    char_stats = await parse_char_stats(max_stats)

    # 命座
    char_chain = await parse_char_chain(char_model.chains)

    card_img = get_waves_bg(1000, char_bg.size[1] + char_chain.size[1] + 50, "bg6")

    char_bg.alpha_composite(char_pic, (0, -100))
    char_bg.alpha_composite(char_stats, (580, 340))
    char_bg.alpha_composite(rarity_pic, (560, 160))
    card_img.paste(char_bg, (0, -5), char_bg)
    card_img.alpha_composite(char_chain, (0, 600))

    card_img = add_footer(card_img, 800, 20, color="hakush")
    card_img = await convert_img(card_img)
    return card_img


async def parse_char_stats(max_stats: Stats):
    labels = ["基础生命", "基础攻击", "基础防御"]
    values = [f"{max_stats.life:.0f}", f"{max_stats.atk:.0f}", f"{max_stats.def_:.0f}"]
    rows = [(label, value) for label, value in zip(labels, values)]

    col_count = sum(len(row) for row in rows)
    cell_width = 400
    cell_height = 40
    table_width = cell_width
    table_height = col_count * cell_height

    image = Image.new("RGBA", (table_width, table_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    # 绘制表格
    for row_index, row in enumerate(rows):
        for col_index, cell in enumerate(row):
            # 计算单元格位置
            x0 = col_index * cell_width / 2
            y0 = row_index * cell_height
            x1 = x0 + cell_width / 2
            y1 = y0 + cell_height

            # 绘制矩形边框
            _i = 0.8 if row_index % 2 == 0 else 1
            draw.rectangle(
                [x0, y0, x1, y1], fill=(40, 40, 40, int(_i * 255)), outline=GREY
            )

            # 计算文本位置以居中
            bbox = draw.textbbox((0, 0), cell, font=waves_font_24)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x0 + (cell_width / 2 - text_width) / 2
            text_y = y0 + (cell_height - text_height) / 2

            # 绘制文本
            draw.text((text_x, text_y), cell, fill="white", font=waves_font_24)

    return image


async def parse_char_chain(data: Dict[int, Chain]):
    y_padding = 20  # 初始位移
    x_padding = 20  # 初始位移
    line_spacing = 10  # 行间距
    block_line_spacing = 50  # 块行间距
    image_width = 1000  # 每个图像的宽度
    shadow_radius = 20  # 阴影半径

    title_color = SPECIAL_GOLD
    title_font_size = 40
    title_font = waves_font_origin(title_font_size)

    detail_color = "white"
    detail_color_size = 30
    detail_font = waves_font_origin(detail_color_size)

    images = []
    for chain_num in data:
        item = data[chain_num]
        # 拼接文本
        title = item.name
        desc = item.get_desc_detail()

        # 分行显示标题
        wrapped_title = textwrap.fill(title, width=20)
        wrapped_desc = textwrap.fill(desc, width=31)

        # 获取每行的宽度，确保不会超过设定的 image_width
        lines_title = wrapped_title.split("\n")
        lines_desc = wrapped_desc.split("\n")

        # 计算总的绘制高度
        total_text_height = y_padding + block_line_spacing + shadow_radius * 2
        total_text_height += len(lines_title) * (
            title_font_size + line_spacing
        )  # 标题部分的总高度
        total_text_height += len(lines_desc) * (
            detail_color_size + line_spacing
        )  # 描述部分的总高度

        img = Image.new(
            "RGBA",
            (image_width, total_text_height),
            color=(255, 255, 255, 0),
        )
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [
                shadow_radius,
                shadow_radius,
                image_width - shadow_radius,
                total_text_height - shadow_radius,
            ],
            fill=(0, 0, 0, int(0.3 * 255)),
        )

        # 绘制标题文本
        y_offset = y_padding + shadow_radius
        x_offset = x_padding + shadow_radius
        for line in lines_title:
            draw.text(
                (x_offset, y_offset),
                line,
                font=title_font,
                fill=title_color,
            )
            y_offset += title_font.size + line_spacing

        y_offset += block_line_spacing

        # 绘制描述文本
        for line in lines_desc:
            draw.text(
                (x_offset, y_offset),
                line,
                font=detail_font,
                fill=detail_color,
            )
            y_offset += detail_font.size + line_spacing

        images.append(img)

    # 拼接所有图像
    total_height = sum(img.height for img in images)
    final_img = Image.new("RGBA", (image_width, total_height), color=(255, 255, 255, 0))

    y_offset = 0
    for img in images:
        final_img.paste(img, (0, y_offset))
        y_offset += img.height

    return final_img


async def parse_char_skill(data: Dict[str, Dict[str, Skill]]):
    y_padding = 20  # 初始位移
    x_padding = 20  # 初始位移
    line_spacing = 10  # 行间距
    block_line_spacing = 20  # 块行间距
    image_width = 1000  # 每个图像的宽度
    shadow_radius = 20  # 阴影半径

    title_color = SPECIAL_GOLD
    title_font_size = 30
    title_font = waves_font_origin(title_font_size)

    detail_color = "white"
    detail_color_size = 14
    detail_font = waves_font_origin(detail_color_size)

    keys = [
        ("常态攻击", "1", ["12", "13"]),
        ("共鸣技能", "2", ["10", "14"]),
        ("共鸣回路", "7", ["4", "5"]),
        ("共鸣解放", "3", ["11", "15"]),
        ("变奏技能", "6", ["9", "16"]),
        ("延奏技能", "8", []),
    ]

    images = []
    for skill_type, skill_tree_id, relate_skill_tree_ids in keys:
        item = data[skill_tree_id]["skill"]

        # 拼接文本
        title = skill_type
        desc = item.get_desc_detail()

        # 分行显示标题
        wrapped_title = textwrap.fill(title, width=10)
        wrapped_desc = wrap_text_with_manual_newlines(desc, width=65)

        # 获取每行的宽度，确保不会超过设定的 image_width
        lines_title = wrapped_title.split("\n")
        lines_desc = wrapped_desc.split("\n")

        for relate_id in relate_skill_tree_ids:
            relate_item = data[relate_id]["skill"]
            _type = relate_item.type if relate_item.type else "属性加成"
            relate_title = f"{_type}: {relate_item.name}"
            relate_desc = relate_item.get_desc_detail()
            wrapped_relate_desc = wrap_text_with_manual_newlines(relate_desc, width=65)

            lines_desc.append(relate_title)
            lines_desc.extend(wrapped_relate_desc.split("\n"))

        # 计算总的绘制高度
        total_text_height = y_padding + block_line_spacing + shadow_radius * 2
        total_text_height += len(lines_title) * (
            title_font_size + line_spacing
        )  # 标题部分的总高度
        total_text_height += len(lines_desc) * (
            detail_color_size + line_spacing
        )  # 描述部分的总高度

        img = Image.new(
            "RGBA",
            (image_width, total_text_height),
            color=(255, 255, 255, 0),
        )
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [
                shadow_radius,
                shadow_radius,
                image_width - shadow_radius,
                total_text_height - shadow_radius,
            ],
            fill=(0, 0, 0, int(0.3 * 255)),
        )

        # 绘制标题文本
        y_offset = y_padding + shadow_radius
        x_offset = x_padding + shadow_radius
        for line in lines_title:
            draw.text(
                (x_offset, y_offset),
                line,
                font=title_font,
                fill=title_color,
            )
            y_offset += title_font.size + line_spacing

        y_offset += block_line_spacing

        # 绘制描述文本
        for line in lines_desc:
            color = (
                title_color
                if line.startswith("属性加成") or line.startswith("固有技能")
                else detail_color
            )
            draw.text(
                (x_offset, y_offset),
                line,
                font=detail_font,
                fill=color,
            )
            y_offset += detail_font.size + line_spacing

        images.append(img)

        skill_rate = await parse_char_skill_rate(item.level)
        if skill_rate:
            images.append(skill_rate)

    # 拼接所有图像
    total_height = sum(img.height for img in images)
    final_img = Image.new("RGBA", (image_width, total_height), color=(255, 255, 255, 0))

    y_offset = 0
    for img in images:
        final_img.paste(img, (0, y_offset))
        y_offset += img.height

    return final_img


async def parse_char_skill_rate(skillLevels: Optional[Dict[str, SkillLevel]]):
    if not skillLevels:
        return
    rows = []
    labels = [
        "等级",
        "Lv 6",
        "Lv 7",
        "Lv 8",
        "Lv 9",
        "Lv 10",
    ]
    rows.append(labels)

    for _, skillLevel in skillLevels.items():
        row = [skillLevel.name]
        row.extend(skillLevel.param[0][5:10])
        rows.append(row)

    font = waves_font_12
    offset = 20
    col_count = len(rows)
    cell_width = 155
    first_col_width = cell_width + 50
    cell_height = 40
    table_width = 1000
    table_height = col_count * cell_height

    image = Image.new("RGBA", (table_width, table_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    # 绘制表格
    for row_index, row in enumerate(rows):
        for col_index, cell in enumerate(row):
            # 计算单元格位置
            if col_index == 0:
                x0 = offset
                x1 = first_col_width
            else:
                x0 = first_col_width + (col_index - 1) * cell_width
                x1 = x0 + cell_width

            y0 = row_index * cell_height
            y1 = y0 + cell_height

            # 绘制矩形边框
            _i = 0.3 if row_index % 2 == 0 else 0.7
            draw.rectangle(
                [x0, y0, x1, y1], fill=(40, 40, 40, int(_i * 255)), outline=GREY
            )

            # 计算文本位置以居中
            bbox = draw.textbbox((0, 0), cell, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            if col_index == 0:
                text_x = (x0 + first_col_width - text_width) / 2
            else:
                text_x = x0 + (cell_width - text_width) / 2
            text_y = y0 + (cell_height - text_height) / 2

            # 绘制文本
            wrapped_cell = textwrap.wrap(cell, width=18)
            if len(wrapped_cell) > 1:
                text_y_temp = text_y - font.size
                for line in wrapped_cell:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    if col_index == 0:
                        text_x = (x0 + first_col_width - text_width) / 2
                    else:
                        text_x = x0 + (cell_width - text_width) / 2
                    draw.text(
                        (text_x, text_y_temp),
                        line,
                        fill="white",
                        font=font,
                    )
                    text_y_temp += font.size + 7
            else:
                draw.text(
                    (text_x, text_y),
                    cell,
                    fill="white",
                    font=font,
                )

    return image


def wrap_text_with_manual_newlines(
    text: str,
    width: int = 70,
) -> str:
    """
    处理文本，优先保留原始文本中的 \n，再使用 textwrap 进行换行。

    :param text: 原始文本
    :param width: 自动换行的宽度
    :return: 处理后的文本
    """
    lines = text.split("\n")
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]
    final_text = "\n".join(wrapped_lines)
    return final_text
