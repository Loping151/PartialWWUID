import textwrap
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw

from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.ascension.echo import get_echo_model
from ..utils.ascension.model import EchoModel
from ..utils.fonts.waves_fonts import (
    waves_font_30,
    waves_font_40,
    waves_font_origin,
)
from ..utils.image import (
    SPECIAL_GOLD,
    add_footer,
    get_attribute_effect,
    get_crop_waves_bg,
)
from ..utils.name_convert import alias_to_echo_name, echo_name_to_echo_id
from ..utils.resource.download_file import get_phantom_img

TEXT_PATH = Path(__file__).parent / "texture2d"


async def parse_echo_base_content(echo_id, echo_model: EchoModel, image, card_img):
    # 提取名称
    echo_name = echo_model.name

    # echo 图片
    echo_pic = await get_phantom_img(echo_id, "")
    echo_pic = crop_center_img(echo_pic, 110, 110)
    echo_pic = echo_pic.resize((250, 250))

    draw = ImageDraw.Draw(image)
    draw.rectangle([20, 20, 330, 380], fill=(0, 0, 0, int(0.4 * 255)))

    image.alpha_composite(echo_pic, (50, 20))

    card_img_draw = ImageDraw.Draw(card_img)
    card_img_draw.text((350, 50), f"{echo_name}", SPECIAL_GOLD, waves_font_40, "lm")

    # 计算echo_name的宽度
    echo_name_width = card_img_draw.textlength(echo_name, waves_font_40) + 350 + 20
    echo_name_width = int(echo_name_width)

    # 合鸣效果
    group_name = echo_model.get_group_name()
    for index, name in enumerate(group_name):
        effect_image = await get_attribute_effect(name)
        effect_image = effect_image.resize((30, 30))
        card_img.alpha_composite(effect_image, (echo_name_width + index * 35, 40))


async def parse_echo_detail_content(echo_model: EchoModel, card_img):
    y_padding = 20  # 初始位移
    x_padding = 20  # 初始位移
    line_spacing = 10  # 行间距
    block_line_spacing = 10  # 块行间距
    shadow_radius = 20  # 阴影半径

    title_color = SPECIAL_GOLD
    title_font_size = 20
    title_font = waves_font_origin(title_font_size)

    detail_color = "white"
    detail_font_size = 14
    detail_font = waves_font_origin(detail_font_size)

    image = Image.new("RGBA", (650, 320), (255, 255, 255, 0))
    image_draw = ImageDraw.Draw(image)
    image_draw.rounded_rectangle(
        [20, 20, 630, 300], radius=20, fill=(0, 0, 0, int(0.3 * 255))
    )
    title = "技能描述"
    desc = echo_model.get_skill_detail()

    # 分行显示标题
    wrapped_title = textwrap.fill(title, width=10)
    # wrapped_desc = textwrap.fill(desc, width=44)
    wrapped_desc = wrap_text_with_manual_newlines(desc, width=44)

    # 获取每行的宽度，确保不会超过设定的 image_width
    lines_title = wrapped_title.split("\n")
    lines_desc = wrapped_desc.split("\n")

    # 计算总的绘制高度
    total_text_height = y_padding + block_line_spacing + shadow_radius * 2
    total_text_height += len(lines_title) * (
        title_font_size + line_spacing
    )  # 标题部分的总高度
    total_text_height += len(lines_desc) * (
        detail_font_size + line_spacing
    )  # 描述部分的总高度

    # 绘制标题文本
    y_offset = y_padding + shadow_radius
    x_offset = x_padding + shadow_radius
    for line in lines_title:
        image_draw.text(
            (x_offset, y_offset),
            line,
            font=title_font,
            fill=title_color,
        )
        y_offset += title_font.size + line_spacing

    y_offset += block_line_spacing

    # 绘制描述文本
    for line in lines_desc:
        image_draw.text(
            (x_offset, y_offset),
            line,
            font=detail_font,
            fill=detail_color,
        )
        y_offset += detail_font.size + line_spacing

    card_img.alpha_composite(image, (330, 80))


async def parse_echo_statistic_content(echo_model: EchoModel, echo_image):
    rows = echo_model.get_intensity()
    echo_bg = Image.open(TEXT_PATH / "weapon_bg.png")
    echo_bg_temp = Image.new("RGBA", echo_bg.size)
    echo_bg_temp.alpha_composite(echo_bg, dest=(0, 0))
    echo_bg_temp_draw = ImageDraw.Draw(echo_bg_temp)
    for index, row in enumerate(rows):
        echo_bg_temp_draw.text(
            (100, 207 + index * 50), f"{row[0]}", "white", waves_font_30, "lm"
        )
        echo_bg_temp_draw.text(
            (480, 207 + index * 50), f"{row[1]}", "white", waves_font_30, "rm"
        )

    echo_bg_temp = echo_bg_temp.resize((350, 175))
    echo_image.alpha_composite(echo_bg_temp, (10, 200))


async def create_image(echo_id, echo_model: EchoModel):
    echo_image = Image.new("RGBA", (350, 400), (255, 255, 255, 0))

    card_img = get_crop_waves_bg(1000, 420, "bg5")
    await parse_echo_base_content(echo_id, echo_model, echo_image, card_img)
    await parse_echo_statistic_content(echo_model, echo_image)
    await parse_echo_detail_content(echo_model, card_img)
    card_img.alpha_composite(echo_image, (0, 0))
    card_img = add_footer(card_img, 800, 20, color="hakush")
    card_img = await convert_img(card_img)
    return card_img


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


async def draw_wiki_echo(echo_name: str):
    echo_name = alias_to_echo_name(echo_name)
    echo_id = echo_name_to_echo_id(echo_name)
    if echo_id is None:
        return None

    echo_model: Optional[EchoModel] = get_echo_model(echo_id)
    if not echo_model:
        return f"[鸣潮] 暂无【{echo_name}】对应wiki"

    card_img = await create_image(echo_id, echo_model)
    return card_img
