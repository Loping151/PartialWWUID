from typing import List, Optional

from pydantic import BaseModel


class LinkConfig(BaseModel):
    linkUrl: Optional[str] = None
    linkType: int
    entryId: str


class ProgressData(BaseModel):
    progressType: int
    dataRange: List[str]
    title: str


class RepeatConfig(BaseModel):
    endDate: str
    isNeverEnd: bool
    repeatInterval: int
    dataRanges: List[ProgressData]


class CountDown(BaseModel):
    dateRange: Optional[List[str]] = None


class ContentData(BaseModel):
    contentUrl: str
    countDown: Optional[CountDown] = None
    title: str


class VersionActivity(BaseModel):
    content: List[ContentData]


class ImageItem(BaseModel):
    linkConfig: LinkConfig
    img: str
    title: str


class SpecialImages(BaseModel):
    name: str
    imgs: List[ImageItem]
