from datetime import datetime

import sqlalchemy as sa


metadata = sa.MetaData()


offset = sa.Table(
    "offset",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(64), nullable=False),
    sa.Column("processed", sa.Integer, nullable=False),
    sa.Column("remaining", sa.Integer, nullable=False),
    sa.Column(
        "requested", sa.TIMESTAMP, nullable=False, default=datetime.utcnow
    ),
)

proxy = sa.Table(
    "proxy",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(64), nullable=False),
    sa.Column("free", sa.Integer, nullable=False),
    sa.Column("used", sa.Integer, nullable=False),
    sa.Column("content_len", sa.Integer, nullable=False),
    sa.Column("messages", sa.Integer, nullable=False),
    sa.Column(
        "requested", sa.TIMESTAMP, nullable=False, default=datetime.utcnow
    ),
)
