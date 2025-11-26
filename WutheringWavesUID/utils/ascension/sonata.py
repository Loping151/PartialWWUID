from pathlib import Path
from typing import Dict, List, Optional, Union

from msgspec import json as msgjson
from pydantic import BaseModel, Field

from gsuid_core.logger import logger

MAP_PATH = Path(__file__).parent.parent / "map/detail_json/sonata"
sonata_id_data = {}


def read_sonata_json_files(directory):
    files = directory.rglob("*.json")

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = msgjson.decode(f.read())
                file_name = file.name.split(".")[0]
                sonata_id_data[file_name] = data
        except Exception as e:
            logger.exception(f"read_char_json_files load fail decoding {file}", e)


read_sonata_json_files(MAP_PATH)


class SonataSet(BaseModel):
    desc: str = Field(default="")
    effect: str = Field(default="")
    param: List[str] = Field(default_factory=list)


class WavesSonataResult(BaseModel):
    name: str = Field(default="")
    set: Dict[str, SonataSet] = Field(default_factory=dict)

    def piece(self, piece_count: Union[str, int]) -> Optional[SonataSet]:
        """获取件套效果"""
        return self.set.get(str(piece_count), None)

    def full_piece_effect(self) -> int:
        """获取套装最大件数"""
        return max(int(key) for key in self.set.keys())


def get_sonata_detail(sonata_name: Optional[str]) -> WavesSonataResult:
    result = WavesSonataResult()
    if sonata_name is None or str(sonata_name) not in sonata_id_data:
        logger.exception(f"get_sonata_detail sonata_name: {sonata_name} not found")
        return result

    return WavesSonataResult(**sonata_id_data[sonata_name])
