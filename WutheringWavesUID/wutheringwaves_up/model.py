from pydantic import BaseModel

"""
{
        "bbs": "https://www.kurobbs.com/mc/post/1353772919378649088",
        "name": "坎特蕾拉",
        "title": "映海之梦",
        "pic": "https://prod-alicdn-community.kurobbs.com/forum/02d2e5e6cc144aeb8462835dc9cbc39620250324.jpeg",
        "five_star_ids": [
            "1607"
        ],
        "five_star_names": [
            "坎特蕾拉"
        ],
        "four_star_ids": [
            "1602",
            "1202",
            "1303"
        ],
        "four_star_names": [
            "丹瑾",
            "炽霞",
            "渊武"
        ],
        "pool_type": "角色活动唤取",
        "start_time": "版本更新时间",
        "end_time": "2025-04-17 09:59:59"
}
"""


class WavesPool(BaseModel):
    bbs: str
    name: str
    title: str
    pic: str
    five_star_ids: list[str]
    five_star_names: list[str]
    four_star_ids: list[str]
    four_star_names: list[str]
    pool_type: str
    start_time: str
    end_time: str
