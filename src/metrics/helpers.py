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


async def get_offset_records_for_each_min(
        interval_min, start_interval, end_interval=None
):
    if end_interval is None:
        end_interval = datetime.now()

    interval_min = interval_min % 60
    interval_number = calculate_intervals(
        start_interval, end_interval, interval_min
    )

    query = sa.select(offset).distinct(
        offset.c.name,
        sa.func.extract('year', offset.c.requested),
        sa.func.extract('month', offset.c.requested),
        sa.func.extract('day', offset.c.requested),
        sa.func.extract('hour', offset.c.requested),
        sa.func.extract('minute', offset.c.requested)
    ).filter(
        offset.c.requested >= start_interval,
        offset.c.requested <= end_interval,
        sa.func.extract('minute', offset.c.requested) % interval_min == 0,
    ).limit(interval_number)

    async with async_session_maker() as session:
        records = await session.execute(query)
    return records.all()


def calculate_intervals(start_datetime, end_datetime, interval_minutes):
    time_difference = end_datetime - start_datetime
    interval_seconds = interval_minutes * 60
    num_intervals = time_difference.total_seconds() // interval_seconds
    return int(num_intervals)


async def get_active_topic_names_for_sec(sec):
    query = sa.select(sa.distinct(offset.c.name)).where(
        offset.c.requested >= datetime.now() - timedelta(seconds=sec)
    )
    async with async_session_maker() as session:
        offsets = await session.execute(query)
    return [name[0] for name in offsets.all()]


async def get_full_history_topics_offsets(
        names,
        appropriate_lag_sec=60 * 60 * 12,
        limit_requested_sec=7 * 24 * 60 * 60,
):
    ...
    # query = (
    #     sa.select(offset)
    #     .where(sa.and_(
    #         offset.c.name.in_(names),
    #         offset.c.requested >= breakpoints_cte.c.requested
    #     ))
    #     .order_by(offset.c.requested.desc())
    # )

    # async with async_session_maker() as session:
    #     offsets = await session.execute(query)
    # return offsets.all()
