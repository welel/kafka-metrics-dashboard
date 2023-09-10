from datetime import datetime, timedelta

import sqlalchemy as sa

from src.db import async_session_maker
from src.metrics.models import offset


async def get_offsets_for_last_sec(sec: int):
    query = sa.select(offset).where(
        offset.c.requested >= datetime.now() - timedelta(seconds=sec)
    ).order_by(offset.c.requested)
    async with async_session_maker() as session:
        offsets = await session.execute(query)
    return offsets.all()
