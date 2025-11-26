import json
from pathlib import Path

import aiofiles

from ..utils.resource.RESOURCE_PATH import PLAYER_PATH

MAP_PATH = Path(__file__).parent / "map"
LIMIT_PATH = MAP_PATH / "1.json"


async def load_limit_user_card():
    async with aiofiles.open(LIMIT_PATH, "r", encoding="UTF-8") as f:
        data = json.loads(await f.read())

    LIMIT_USER_PATH = PLAYER_PATH / "1"
    if not LIMIT_USER_PATH.exists():
        LIMIT_USER_PATH.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(
        LIMIT_USER_PATH / "rawData.json", "w", encoding="UTF-8"
    ) as f:
        await f.write(json.dumps(data, ensure_ascii=False))

    return data
