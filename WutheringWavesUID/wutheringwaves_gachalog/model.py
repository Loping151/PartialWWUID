from typing import List

from pydantic import BaseModel

"""
{
    "info": {
        "export_time": "2025-03-30 14:40:55",
        "export_app": "WutheringWavesUID",
        "export_app_version": "2.0.1",
        "export_timestamp": 1743316856,
        "version": "v1.0",
        "uid": "101449780"
    },
    "list": [
        {
            "cardPoolType": "角色精准调谐",
            "resourceId": 21010043,
            "qualityLevel": 3,
            "resourceType": "武器",
            "name": "远行者长刃·辟路",
            "count": 1,
            "time": "2025-03-27 10:19:52"
        },
"""


class WWUIDGachaInfo(BaseModel):
    export_time: str
    export_app: str
    export_app_version: str
    export_timestamp: int
    version: str
    uid: str


class WWUIDGachaItem(BaseModel):
    cardPoolType: str
    resourceId: int
    qualityLevel: int
    resourceType: str
    name: str
    count: int
    time: str


class WWUIDGacha(BaseModel):
    info: WWUIDGachaInfo
    list: List[WWUIDGachaItem]
