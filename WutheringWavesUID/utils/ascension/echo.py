from pathlib import Path
from typing import Optional, Union

from msgspec import json as msgjson

from gsuid_core.logger import logger

from .model import EchoModel

MAP_PATH = Path(__file__).parent.parent / "map/detail_json/echo"
echo_id_data = {}


def read_echo_json_files(directory):
    files = directory.rglob("*.json")

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = msgjson.decode(f.read())
                file_name = file.name.split(".")[0]
                echo_id_data[file_name] = data
        except Exception as e:
            logger.exception(f"read_echo_json_files load fail decoding {file}", e)


read_echo_json_files(MAP_PATH)


def get_echo_model(echo_id: Union[int, str]) -> Optional[EchoModel]:
    if str(echo_id) not in echo_id_data:
        return None
    return EchoModel(**echo_id_data[str(echo_id)])
