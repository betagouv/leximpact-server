"""create_user

Revision ID: fbddd9e181d5
Revises:
Create Date: 2019-07-18 14:24:41.319556

"""
from alembic.op import create_table, drop_table  # type: ignore
from sqlalchemy import Column, String, DateTime, Integer  # type: ignore


# revision identifiers, used by Alembic.
revision = "fbddd9e181d5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    create_table("users", Column("email", String(), primary_key=True))
    create_table(
        "requests",
        Column("id", Integer, primary_key=True),
        Column("email", String()),
        Column("timestamp", DateTime()),
    )


def downgrade():
    drop_table("users")
    drop_table("requests")
