from datetime import datetime
from typing import List

from pydantic import BaseModel

from .model import WWUIDGacha, WWUIDGachaInfo, WWUIDGachaItem

"""
{
  "info": {
    "lang": "zh-cn",
    "region_time_zone": 8,
    "export_timestamp": 1739420277878,
    "export_app": "Waves-Plugin",
    "export_app_version": "1.5.17",
    "wwgf_version": "v0.1b",
    "uid": "101356589"
  },
  "list": [
    {
      "gacha_id": "0001",
      "gacha_type": "角色活动唤取",
      "item_id": "21040043",
      "count": "1",
      "time": "2025-02-13 10:08:05",
      "name": "远行者臂铠·破障",
      "item_type": "武器",
      "rank_type": "3",
      "id": "1739412485000100010"
    },
"""

turn_kuro_gacha_type = {
    "角色活动唤取": "角色精准调谐",
    "武器活动唤取": "武器精准调谐",
    "角色常驻换取": "角色调谐（常驻池）",
    "武器常驻唤取": "武器调谐（常驻池）",
}


class WavesPluginGachaInfo(BaseModel):
    lang: str
    region_time_zone: int
    export_timestamp: int
    export_app: str
    export_app_version: str
    wwgf_version: str
    uid: str


class WavesPluginGachaItem(BaseModel):
    gacha_id: str
    gacha_type: str
    item_id: str
    count: str
    time: str
    name: str
    item_type: str
    rank_type: str
    id: str


class WavesPluginGacha(BaseModel):
    info: WavesPluginGachaInfo
    list: List[WavesPluginGachaItem]

    def turn_wwuid_gacha(self) -> WWUIDGacha:
        export_timestamp = int(self.info.export_timestamp / 1000)
        export_time = datetime.fromtimestamp(export_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return WWUIDGacha(
            info=WWUIDGachaInfo(
                export_time=export_time,
                export_app=self.info.export_app,
                export_app_version=self.info.export_app_version,
                export_timestamp=export_timestamp,
                version=self.info.wwgf_version,
                uid=self.info.uid,
            ),
            list=[
                WWUIDGachaItem(
                    cardPoolType=turn_kuro_gacha_type.get(
                        item.gacha_type, item.gacha_type
                    ),
                    resourceId=int(item.item_id),
                    qualityLevel=int(item.rank_type),
                    resourceType=item.item_type,
                    name=item.name,
                    count=int(item.count),
                    time=item.time,
                )
                for item in self.list
            ],
        )
