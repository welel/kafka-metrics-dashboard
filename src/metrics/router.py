import logging
from datetime import datetime, timedelta

from fastapi import APIRouter

from src.metrics.formatters import format_graph_init_values

from .calculation import get_offset_reports
from .helpers import (
    get_offsets_for_last_sec,
    get_offset_records_for_each_min,
)
from .schemas import OffsetReport, OffsetGraphInit
from servers.metrics.client import MetricsClient
from servers.metrics.schemas import OffsetsMetrics


router = APIRouter(prefix="/metrics", tags=["Metrics"])
metrics_client = MetricsClient("localhost", 6000)
logger = logging.getLogger(__name__)


# @router.get("/offsets", response_model=dict[str, OffsetReport])
# async def get_last_offset(sec: int = 60 * 10):
#     try:
#         offsets = await get_offsets_for_last_sec(sec)
#         return await get_offset_reports(offsets)
#     except Exception as e:
#         logger.error("Server Error: %s", e, exc_info=True)


@router.get("/offsets", response_model=OffsetsMetrics)
async def get_offests(sec: int = 60 * 10):
    try:
        return metrics_client.get_dashboard_data()
    except Exception as e:
        logger.error("Server Error: %s", e, exc_info=True)


@router.get("/graph", response_model=dict[str, OffsetGraphInit])
async def get_graph_init_values():
    try:
        end = datetime.now()
        start = datetime.now() - timedelta(hours=6)
        offsets = await get_offset_records_for_each_min(5, start, end)
        return format_graph_init_values(offsets)
    except Exception as e:
        logger.error("Server Error: %s", e, exc_info=True)
