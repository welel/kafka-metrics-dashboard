import logging

from fastapi import APIRouter

from servers.metrics.client import MetricsClient
from servers.metrics.schemas import OffsetsMetrics

from settings import METRICS_SERVER_HOST, METRICS_SERVER_PORT


router = APIRouter(prefix="/metrics", tags=["Metrics"])
metrics_client = MetricsClient(METRICS_SERVER_HOST, METRICS_SERVER_PORT)
logger = logging.getLogger(__name__)


@router.get("/dashboard", response_model=OffsetsMetrics)
async def get_offests():
    try:
        data = metrics_client.get_dashboard_data()
        if data is None:
            raise ValueError("Invalid respose from the metrics server.")
        return data
    except Exception as e:
        logger.error("Server Error: %s", e, exc_info=True)
