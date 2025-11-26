import textwrap
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw

from gsuid_core.utils.image.convert import convert_img
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.ascension.model import WeaponModel
from ..utils.ascension.weapon import (
    get_weapon_id,
    get_weapon_model,
    get_weapon_star,
)
from ..utils.fonts.waves_fonts import (
    waves_font_30,
    waves_font_40,
    waves_font_origin,
)
from ..utils.image import (
    SPECIAL_GOLD,
    add_footer,
    get_attribute_prop,
    get_crop_waves_bg,
    get_square_weapon,
    get_weapon_type,
)
from ..utils.name_convert import alias_to_weapon_name
from ..utils.resource.download_file import get_material_img

TEXT_PATH = Path(__file__).parent / "texture2d"


async def parse_weapon_base_content(
    weapon_id, weapon_model: WeaponModel, image, card_img
):
    # 提取名称
    weapon_name = weapon_model.name

    # 提取“武器类型”
    weapon_type = weapon_model.get_weapon_type()

    # 提取“稀有度”
    rarity_pic = Image.open(TEXT_PATH / f"rarity_{weapon_model.starLevel}.png")
    rarity_pic = rarity_pic.resize(
        (180, int(180 / rarity_pic.size[0] * rarity_pic.size[1]))
    )
    # weapon 图片
    weapon_pic = await get_square_weapon(weapon_id)
    weapon_pic = crop_center_img(weapon_pic, 110, 110)
    weapon_pic_bg = get_weapon_icon_bg(get_weapon_star(weapon_name))
    weapon_pic_bg.paste(weapon_pic, (10, 20), weapon_pic)
    weapon_pic_bg = weapon_pic_bg.resize((250, 250))

    draw = ImageDraw.Draw(image)
    draw.rectangle([20, 20, 330, 380], fill=(0, 0, 0, int(0.4 * 255)))

    image.alpha_composite(weapon_pic_bg, (50, 20))

    weapon_type = await get_weapon_type(weapon_type)
    weapon_type = weapon_type.resize((80, 80)).convert("RGBA")
    card_img_draw = ImageDraw.Draw(card_img)
    card_img_draw.text((420, 100), f"{weapon_name}", SPECIAL_GOLD, waves_font_40, "lm")
    card_img.alpha_composite(rarity_pic, (400, 20))
    card_img.alpha_composite(weapon_type, (340, 40))


async def parse_weapon_statistic_content(weapon_model: WeaponModel, weapon_image):
    rows = weapon_model.get_max_level_stat_tuple()
    weapon_bg = Image.open(TEXT_PATH / "weapon_bg.png")
    weapon_bg_temp = Image.new("RGBA", weapon_bg.size)
    weapon_bg_temp.alpha_composite(weapon_bg, dest=(0, 0))
    weapon_bg_temp_draw = ImageDraw.Draw(weapon_bg_temp)
    for index, row in enumerate(rows):
        stats_main = await get_attribute_prop(row[0])
        stats_main = stats_main.resize((40, 40))
        weapon_bg_temp.alpha_composite(stats_main, (65, 187 + index * 50))
        weapon_bg_temp_draw.text(
            (130, 207 + index * 50), f"{row[0]}", "white", waves_font_30, "lm"
        )
        weapon_bg_temp_draw.text(
            (500, 207 + index * 50), f"{row[1]}", "white", waves_font_30, "rm"
        )

    weapon_bg_temp = weapon_bg_temp.resize((350, 175))
    weapon_image.alpha_composite(weapon_bg_temp, (10, 200))


async def parse_weapon_material_content(weapon_model: WeaponModel, card_img):
    material_img = Image.new("RGBA", (300, 150))
    material_img_draw = ImageDraw.Draw(material_img)
    material_img_draw.rounded_rectangle(
        [20, 20, 280, 130], radius=20, fill=(0, 0, 0, int(0.3 * 255))
    )
    material_img_draw.text(
        (40, 20), "突破材料", SPECIAL_GOLD, waves_font_origin(24), "lm"
    )
    index = 0
    for material_id in weapon_model.get_ascensions_max_list():
        material = await get_material_img(material_id)
        if not material:
            continue
        material = material.resize((70, 70))
        material_img.alpha_composite(material, (30 + index * 80, 50))
        index += 1

    card_img.alpha_composite(material_img, (680, 15))


async def parse_weapon_detail_content(weapon_model: WeaponModel, card_img):
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

    image = Image.new("RGBA", (650, 270), (255, 255, 255, 0))
    image_draw = ImageDraw.Draw(image)
    image_draw.rounded_rectangle(
        [20, 20, 630, 250], radius=20, fill=(0, 0, 0, int(0.3 * 255))
    )
    title = weapon_model.effectName
    desc = weapon_model.get_effect_detail()

    # 分行显示标题
    wrapped_title = textwrap.fill(title, width=10)
    wrapped_desc = textwrap.fill(desc, width=44)

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

    card_img.alpha_composite(image, (330, 130))


async def create_image(weapon_id, weapon_model: WeaponModel):
    weapon_image = Image.new("RGBA", (350, 400), (255, 255, 255, 0))

    card_img = get_crop_waves_bg(1000, 420, "bg5")
    await parse_weapon_base_content(weapon_id, weapon_model, weapon_image, card_img)
    await parse_weapon_statistic_content(weapon_model, weapon_image)
    await parse_weapon_detail_content(weapon_model, card_img)
    await parse_weapon_material_content(weapon_model, card_img)
    card_img.alpha_composite(weapon_image, (0, 0))
    card_img = add_footer(card_img, 800, 20, color="hakush")
    card_img = await convert_img(card_img)
    return card_img


def get_weapon_icon_bg(star: int = 3) -> Image.Image:
    if star < 3:
        star = 3
    bg_path = TEXT_PATH / f"weapon_icon_bg_{star}.png"
    bg_img = Image.open(bg_path)
    bg_img = Image.new("RGBA", bg_img.size)
    return bg_img


async def draw_wiki_weapon(weapon_name: str):
    weapon_name = alias_to_weapon_name(weapon_name)
    weapon_id = get_weapon_id(weapon_name)
    if weapon_id is None:
        return None

    weapon_model: Optional[WeaponModel] = get_weapon_model(weapon_id)
    if not weapon_model:
        return f"[鸣潮] 暂无【{weapon_name}】对应wiki"

    card_img = await create_image(weapon_id, weapon_model)
    return card_img
