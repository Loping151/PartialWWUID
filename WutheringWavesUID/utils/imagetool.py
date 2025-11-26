from pathlib import Path

from PIL import Image
from gsuid_core.models import Event
from gsuid_core.utils.image.image_tools import crop_center_img

from ..utils.image import get_event_avatar, get_square_avatar

TEXT_PATH = Path(__file__).parent / "texture2d"


async def draw_pic_with_ring(ev: Event):
    pic = await get_event_avatar(ev)

    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    avatar = Image.new("RGBA", (180, 180))
    mask = mask_pic.resize((160, 160))
    resize_pic = crop_center_img(pic, 160, 160)
    avatar.paste(resize_pic, (20, 20), mask)

    avatar_ring = Image.open(TEXT_PATH / "avatar_ring.png")
    avatar_ring = avatar_ring.resize((180, 180))
    return avatar, avatar_ring


async def draw_pic(roleId):
    pic = await get_square_avatar(roleId)
    mask_pic = Image.open(TEXT_PATH / "avatar_mask.png")
    img = Image.new("RGBA", (180, 180))
    mask = mask_pic.resize((140, 140))
    resize_pic = crop_center_img(pic, 140, 140)
    img.paste(resize_pic, (22, 18), mask)

    return img
