"""create_user

Revision ID: fbddd9e181d5
Revises:
Create Date: 2019-07-18 14:24:41.319556

"""
from alembic.op import create_table, drop_table  # type: ignore
from sqlalchemy import Column, String  # type: ignore


# revision identifiers, used by Alembic.
revision = "fbddd9e181d5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    create_table(
        "users", Column("email", String(), primary_key=True), Column("token", String())
    )


def downgrade():
    drop_table("users")
