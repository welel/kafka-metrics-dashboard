from datetime import datetime, timedelta

import sqlalchemy as sa

from src.db import session_maker
from src.metrics.models import offset


def get_full_history_topic_offsets(
        name,
        appropriate_lag_sec=60 * 60 * 12,
        limit_requested_sec=7 * 24 * 60 * 60,
):
    """

    Args:
        name (str): The topic name.
        appropriate_lag_sec (int): The appropriate interval between fresh
            data and first data after unknown period of time.
        limit_requested_sec (int): Filter offsets by the `requested` field,
            selects all from now minus `limit_requested_sec`.
    """
    breakpoints_data_cte = (
        sa.select(
            (offset.c.processed + offset.c.remaining - sa.func.lag(
                offset.c.processed + offset.c.remaining).over(
                    order_by=(offset.c.requested))).label('gap_total'),
            sa.extract('epoch', offset.c.requested - sa.func.lag(
                offset.c.requested).over(
                    order_by=offset.c.requested)).label('gap_sec'),
            offset.c.requested,
            offset.c.name
        )
        .where(sa.and_(
            offset.c.name == name,
            offset.c.requested >= datetime.now() - timedelta(
                seconds=limit_requested_sec)
        ))
        .order_by(offset.c.requested.desc())
        .cte('BreakPointsData')
    )

    requested_breakpoint_query = (
        sa.select(breakpoints_data_cte.c.requested)
        .where(sa.or_(
                breakpoints_data_cte.c.gap_total < 0,
                breakpoints_data_cte.c.gap_sec > appropriate_lag_sec
        ))
        .order_by(breakpoints_data_cte.c.requested.desc())
        .limit(1)
    )

    with session_maker() as session:
        breakpoint = session.execute(requested_breakpoint_query)

    breakpoint = breakpoint.first()
    if breakpoint is None:
        print(name, "skipped")
        return
    else:
        breakpoint = breakpoint[0]

    query = (
        sa.select(
            offset.c.processed,
            offset.c.remaining,
            offset.c.requested,
            sa.extract('epoch', offset.c.requested - sa.func.lag(
                offset.c.requested).over(
                    order_by=offset.c.requested)).label('gap_sec'),
            sa.func.lag(offset.c.processed).over(order_by=(
                offset.c.requested)).label('prev_processed'),
            sa.func.lag(offset.c.remaining).over(order_by=(
                offset.c.requested)).label('prev_remaining'),
        )
        .where(sa.and_(
            offset.c.name == name,
            offset.c.requested >= breakpoint
        ))
        .order_by(offset.c.requested.desc())
    )

    with session_maker() as session:
        offsets = session.execute(query)
        return offsets.all()


def get_active_topic_names_for_sec(sec):
    query = sa.select(sa.distinct(offset.c.name)).where(
        offset.c.requested >= datetime.now() - timedelta(seconds=sec)
    )
    with session_maker() as session:
        offsets = session.execute(query)
        return [name[0] for name in offsets.all()]
