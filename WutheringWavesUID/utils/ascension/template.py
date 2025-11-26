import json
from pathlib import Path

import aiofiles

CHAR_TEMPLATE_PATH = Path(__file__).parent.parent / "map/templata.json"


async def get_template_data():
    async with aiofiles.open(CHAR_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return json.loads(await f.read())
