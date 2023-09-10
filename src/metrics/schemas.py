import enum

from datetime import datetime

from pydantic import BaseModel


class TopicStatus(str, enum.Enum):
    ACTIVE = "active"
    DONE = "done"
    DEAD = "dead"


class OffsetReport(BaseModel):
    processed: int
    remaining: int
    total: int
    requested: datetime
    load_speed: int | float | None
    processing_speed: int | float | None
    processed_precent: int | float
    time_left: int | float | str
    entry: int
    status: TopicStatus
    label: str
    name: str
