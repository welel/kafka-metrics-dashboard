import enum
import typing

from datetime import datetime

from pydantic import BaseModel


class ResponseStatus(str, enum.Enum):
    OK = "ok"
    ERROR = "error"
    INVALID = "invalid"


class Request(BaseModel):
    command: str
    data: dict | None = None


class Response(BaseModel):
    status: ResponseStatus
    data: dict = {}
    message: str = ""


class TopicStatus(str, enum.Enum):
    ACTIVE = "active"
    DONE = "done"
    DEAD = "dead"


class LineGraph(BaseModel):
    labels: list[str]
    lines: dict[str, list[typing.Any]]


class OffsetMetrics(BaseModel):
    name: str
    total: int
    processed: int
    queued: int
    processed_precent: int | float
    current_load_speed: int | float | None
    current_processing_speed: int | float | None
    last_requested: datetime
    time_left: int | float | str
    status: TopicStatus
    started: datetime
    finishes: datetime | str
    full_tasks_graphs: LineGraph | None
    full_speeds_graphs: LineGraph | None


class Totals(BaseModel):
    total: int = 0
    processed: int = 0
    queued: int = 0
    active: int = 0
    dead: int = 0
    done: int = 0


class OffsetsMetrics(BaseModel):
    metrics: dict[str, OffsetMetrics]
    totals: Totals
