import logging

from fastapi import APIRouter

from .calculation import offset_reports
from .helpers import get_offsets_for_last_sec
from .schemas import OffsetReport


router = APIRouter(prefix="/metrics", tags=["Metrics"])
logger = logging.getLogger(__name__)


@router.get("/offsets", response_model=dict[str, OffsetReport])
async def get_last_offset(sec: int = 60 * 10):
    try:
        offsets = await get_offsets_for_last_sec(sec)
        return await offset_reports(offsets)
    except Exception as e:
        logger.error("Server Error: %s", e, exc_info=1)
