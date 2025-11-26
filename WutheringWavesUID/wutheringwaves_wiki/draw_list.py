import copy
import textwrap
from pathlib import Path
from collections import defaultdict
from PIL import Image, ImageDraw

from gsuid_core.utils.image.convert import convert_img
from gsuid_core.logger import logger

from ..wutheringwaves_config import PREFIX
from ..utils.ascension.sonata import sonata_id_data
from ..utils.ascension.weapon import weapon_id_data
from ..utils.fonts.waves_fonts import waves_font_24, waves_font_18, waves_font_16
from ..utils.image import (
    SPECIAL_GOLD, 
    get_waves_bg, 
    add_footer, 
    get_attribute_effect, 
    get_square_weapon,
)

TEXT_PATH = Path(__file__).parent.parent / "wutheringwaves_develop" / "texture2d"
star_1 = Image.open(TEXT_PATH / "star-1.png")
star_2 = Image.open(TEXT_PATH / "star-2.png")
star_3 = Image.open(TEXT_PATH / "star-3.png")
star_4 = Image.open(TEXT_PATH / "star-4.png")
star_5 = Image.open(TEXT_PATH / "star-5.png")
star_img_map = {
    1: star_1,
    2: star_2,
    3: star_3,
    4: star_4,
    5: star_5,
}

async def draw_weapon_list(weapon_type: str):
    # 确保数据已加载
    if not weapon_id_data:
        return "[鸣潮][武器列表]暂无数据"
        
    # 武器类型映射
    weapon_type_map = {
        1: "长刃",
        2: "迅刀",
        3: "佩枪",
        4: "臂铠",
        5: "音感仪",
    }
    
    # 创建反向映射（中文类型 → 数字类型）
    reverse_type_map = {v: k for k, v in weapon_type_map.items()}
    logger.debug(f"正在处理武器类型：{weapon_type}")
    logger.debug(f"正在处理武器列表：{reverse_type_map}")
    
    # 按武器类型分组收集武器数据
    weapon_groups = defaultdict(list)
    target_type = reverse_type_map.get(weapon_type)
    logger.debug(f"成功处理：{target_type}")
    
    for weapon_id, data in weapon_id_data.items():
        name = data.get("name", "未知武器")
        star_level = data.get("starLevel", 0)
        w_type = data.get("type", 0)  # 注意：避免与参数同名冲突
        effect_name = data.get("effectName", "")
        
        # 如果找到目标类型，只收集该类型武器
        if target_type is not None:
            if w_type == target_type:
                weapon_groups[w_type].append({
                    "id": weapon_id,
                    "name": name,
                    "star_level": star_level,
                    "effect_name": effect_name
                })
        # 否则收集所有武器
        else:
            weapon_groups[w_type].append({
                "id": weapon_id,
                "name": name,
                "star_level": star_level,
                "effect_name": effect_name
            })
    
    # 按类型从小到大排序
    sorted_groups = sorted(weapon_groups.items(), key=lambda x: x[0])
    
    # 每行武器数量（单类型4列，全部类型9列）
    weapons_per_row = 9 if target_type is None else 4
    # 图标大小
    icon_size = 120
    # 水平间距
    horizontal_spacing = 150

    # 创建更宽的背景图（1800宽度）
    width = horizontal_spacing * (weapons_per_row -1) + icon_size + 80
    img = get_waves_bg(width, 4000, "bg6")
    draw = ImageDraw.Draw(img)
    
    # 绘制标题
    title = "武器一览"
    draw.text((int(width / 2), 30), title, font=waves_font_24, fill=SPECIAL_GOLD, anchor="mt")
    draw.text((int(width / 2), 63),f"使用【{PREFIX}'武器名'图鉴】查询具体介绍",font=waves_font_16, fill="#AAAAAA", anchor="mt")
    
    # 当前绘制位置
    y_offset = 80

    # 添加组间分隔线
    draw.line((40, y_offset, width - 40, y_offset), fill=SPECIAL_GOLD, width=1)
    # 绘制武器效果名（灰色）y_offset += 20
    
    # 按武器类型遍历所有分组
    for weapon_type, weapons in sorted_groups:
        # 获取类型名称
        type_name = weapon_type_map.get(weapon_type, f"未知类型{weapon_type}")
        
        # 绘制类型标题
        draw.text((50, y_offset), type_name, font=waves_font_24, fill=SPECIAL_GOLD)
        y_offset += 40
        
        # 按星级降序排序（高星在前）
        weapons.sort(key=lambda x: (-x["star_level"], x["name"]))
        
        # 计算该组需要的行数
        rows = (len(weapons) + weapons_per_row - 1) // weapons_per_row
        
        # 计算图标和名称的高度
        name_height = 25
        effect_name_height = 20
        row_height = icon_size + name_height + effect_name_height + 30
        
        # 绘制武器组
        for row in range(rows):
            row_y = y_offset # 当前行起始位置
            
            # 绘制该行所有武器
            for col in range(weapons_per_row):
                index = row * weapons_per_row + col
                if index >= len(weapons):
                    break
                
                weapon = weapons[index]
                
                # 计算位置（居中布局）
                x_pos = 40 + col * horizontal_spacing
                
                # 获取武器图标
                weapon_icon = await get_square_weapon(weapon["id"])
                weapon_icon = weapon_icon.resize((icon_size, icon_size))
                    
                # 获取并调整武器背景框
                star_img = copy.deepcopy(star_img_map[weapon["star_level"]])
                star_img = star_img.resize((icon_size, icon_size))
                img.alpha_composite(weapon_icon, (x_pos, row_y))
                img.alpha_composite(star_img, (x_pos, row_y))
                    
                # 绘制武器名称
                draw.text(
                    (x_pos + icon_size // 2, row_y + icon_size + 10),
                    weapon["name"],
                    font=waves_font_18,
                    fill="white",
                    anchor="mt"
                )
                    
                # 绘制武器效果名（灰色）
                draw.text(
                    (x_pos + icon_size // 2, row_y + icon_size + 35),
                    weapon["effect_name"],
                    font=waves_font_16,
                    fill="#AAAAAA",  # 灰色                        
                    anchor="mt"
                )
            
            # 移动到下一行
            y_offset += row_height
        
        # 添加组间分隔线
        draw.line((40, y_offset, width - 40, y_offset), fill=SPECIAL_GOLD, width=1)
        y_offset += 20
    
    # 裁剪图片到实际高度
    img = img.crop((0, 0, width, y_offset + 50))
    img = add_footer(img, int(width / 2), 10)  # 页脚居中
    return await convert_img(img)

async def draw_sonata_list():
    # 确保数据已加载
    if not sonata_id_data:
        return "[鸣潮][套装列表]暂无数据"
    
    # 收集所有声骸套装数据
    sonata_groups = defaultdict(list)
    for data in sonata_id_data.values():
        name = data.get("name", "未知套装")
        set_list = data.get("set", {})
        # 按名称字数分组
        word_count = len(name)
        sonata_groups[word_count].append({
            "name": name,
            "set": set_list
        })
    
    # 按字数从小到大排序
    sorted_groups = sorted(sonata_groups.items(), key=lambda x: x[0])
    
    # 创建背景图（高度暂定，后面会调整）
    img = get_waves_bg(900, 3000, "bg6")
    draw = ImageDraw.Draw(img)
    
    # 绘制标题
    title = "声骸套装一览"
    draw.text((440, 30), title, font=waves_font_24, fill=SPECIAL_GOLD, anchor="mt")

    # 当前绘制位置
    y_offset = 80
    col_width = 18  # 列宽（用于文本换行计算）
    des_height = 25  # 套装效果描述高度

    # 添加组间分隔线
    draw.line((40, y_offset, 860, y_offset), fill=SPECIAL_GOLD, width=1)
    y_offset += 20
    
    # 按字数从小到大遍历所有分组
    for word_count, sonatas in sorted_groups:
        # 对组内套装按名称排序
        sonatas.sort(key=lambda x: x["name"])
        
        # 将组内套装分成两列展示
        for i in range(0, len(sonatas), 2):
            current_y = y_offset  # 记录当前行的起始Y位置
            max_height = 0  # 记录当前行最大高度（用于移动到下一行）
            
            # 第一列套装
            sonata1 = sonatas[i]
            name_height = 30
            
            # 获取套装图标
            fetter_icon1 = await get_attribute_effect(sonata1["name"])
            fetter_icon1 = fetter_icon1.resize((50, 50))
            img.paste(fetter_icon1, (40, current_y), fetter_icon1)
            
            # 绘制套装名称
            draw.text((100, current_y), sonata1["name"], font=waves_font_24, fill=SPECIAL_GOLD)
            
            # 绘制所有套装效果
            current_height = current_y + name_height
            for set_num, effect in sorted(sonata1["set"].items(), key=lambda x: int(x[0])):
                # 绘制件数标签
                draw.text((100, current_height), f"{set_num}件:", font=waves_font_16, fill="white")
                
                # 处理效果描述文本
                desc = effect.get("desc", "")
                wrapped_desc = textwrap.wrap(desc, width=col_width)
                
                # 绘制效果描述
                for j, line in enumerate(wrapped_desc):
                    draw.text((140, current_height + j * des_height), line, font=waves_font_16, fill="#AAAAAA")
                
                # 更新当前高度
                current_height += len(wrapped_desc) * des_height + 5  # 加5像素作为间距
            
            # 计算当前套装总高度
            sonata1_height = current_height - current_y
            max_height = max(max_height, sonata1_height)
            
            # 第二列套装（如果有）
            if i + 1 < len(sonatas):
                sonata2 = sonatas[i + 1]
                
                # 获取套装图标
                fetter_icon2 = await get_attribute_effect(sonata2["name"])
                fetter_icon2 = fetter_icon2.resize((50, 50))
                img.paste(fetter_icon2, (460, current_y), fetter_icon2)
                
                # 绘制套装名称
                draw.text((520, current_y), sonata2["name"], font=waves_font_24, fill=SPECIAL_GOLD)
                
                # 绘制所有套装效果
                current_height2 = current_y + name_height
                for set_num, effect in sorted(sonata2["set"].items(), key=lambda x: int(x[0])):
                    # 绘制件数标签
                    draw.text((520, current_height2), f"{set_num}件:", font=waves_font_16, fill="white")
                    
                    # 处理效果描述文本
                    desc = effect.get("desc", "")
                    wrapped_desc = textwrap.wrap(desc, width=col_width)
                    
                    # 绘制效果描述
                    for j, line in enumerate(wrapped_desc):
                        draw.text((560, current_height2 + j * des_height), line, font=waves_font_16, fill="#AAAAAA")
                    
                    # 更新当前高度
                    current_height2 += len(wrapped_desc) * des_height + 5  # 加5像素作为间距
                
                # 计算当前套装总高度
                sonata2_height = current_height2 - current_y
                max_height = max(max_height, sonata2_height)
            
            # 移动到下一行（使用当前行最大高度 + 间距）
            y_offset += max_height + 20  # 增加行间距
        
        # 添加组间分隔线
        draw.line((40, y_offset, 860, y_offset), fill=SPECIAL_GOLD, width=1)
        y_offset += 20
    
    # 裁剪图片到实际高度
    img = img.crop((0, 0, 900, y_offset + 50))
    img = add_footer(img, 450, 10)
    return await convert_img(img)