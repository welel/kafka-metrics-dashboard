import logging

from fastapi import APIRouter

from servers.metrics.client import MetricsClient
from servers.metrics.schemas import OffsetsMetrics


router = APIRouter(prefix="/metrics", tags=["Metrics"])
metrics_client = MetricsClient("localhost", 6000)
logger = logging.getLogger(__name__)


@router.get("/dashboard", response_model=OffsetsMetrics)
async def get_offests():
    try:
        return metrics_client.get_dashboard_data()
    except Exception as e:
        logger.error("Server Error: %s", e, exc_info=True)
