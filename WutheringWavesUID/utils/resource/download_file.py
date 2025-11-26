from typing import Union

from PIL import Image

from gsuid_core.utils.download_resource.download_file import download

from .RESOURCE_PATH import (
    FETTER_PATH,
    MATERIAL_PATH,
    PHANTOM_PATH,
    ROLE_DETAIL_CHAINS_PATH,
    ROLE_DETAIL_SKILL_PATH,
)


async def get_skill_img(
    char_id: Union[str, int], skill_name: str, pic_url: str
) -> Image.Image:
    _dir = ROLE_DETAIL_SKILL_PATH / str(char_id)
    _dir.mkdir(parents=True, exist_ok=True)

    skill_name = skill_name.strip()
    name = f"skill_{skill_name}.png"
    _path = _dir / name
    if not _path.exists():
        if pic_url:
            await download(pic_url, _dir, name, tag="[鸣潮]")
        else:
            # logger.warning(f"[鸣潮] 角色 {char_id} 的技能图片不存在，使用默认图片")
            _path = ROLE_DETAIL_SKILL_PATH / "1102/skill_1102.png"

    return Image.open(_path).convert("RGBA")


async def get_chain_img(
    char_id: Union[str, int], order_id: int, pic_url: str
) -> Image.Image:
    _dir = ROLE_DETAIL_CHAINS_PATH / str(char_id)
    _dir.mkdir(parents=True, exist_ok=True)

    name = f"chain_{order_id}.png"
    _path = _dir / name
    if not _path.exists():
        if pic_url:
            await download(pic_url, _dir, name, tag="[鸣潮]")
        else:
            # logger.warning(f"[鸣潮] 角色 {char_id} 的共鸣链图片不存在，使用默认图片")
            _path = ROLE_DETAIL_CHAINS_PATH / f"1102/chain_{order_id}.png"

    return Image.open(_path).convert("RGBA")


async def get_phantom_img(phantom_id: int, pic_url: str) -> Image.Image:
    name = f"phantom_{phantom_id}.png"
    _path = PHANTOM_PATH / name
    if not _path.exists():
        if pic_url:
            await download(pic_url, PHANTOM_PATH, name, tag="[鸣潮]")
        else:
            _path = PHANTOM_PATH / "phantom_390070051.png"

    return Image.open(_path).convert("RGBA")


async def get_fetter_img(name: str, pic_url: str) -> Image.Image:
    name = f"fetter_{name}.png"
    _path = FETTER_PATH / name
    if not _path.exists():
        await download(pic_url, FETTER_PATH, name, tag="[鸣潮]")

    return Image.open(_path).convert("RGBA")


async def get_material_img(material_id: Union[str, int]) -> Image.Image:
    name = f"material_{material_id}.png"
    _path = MATERIAL_PATH / name
    return Image.open(_path).convert("RGBA")
