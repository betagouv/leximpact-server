"""create suspended table

Revision ID: 700a389cb5e1
Revises: fbddd9e181d5
Create Date: 2019-08-06 01:00:44.945105

"""
from alembic.op import create_table, drop_table
from sqlalchemy import Column, String, DateTime, Integer


# revision identifiers, used by Alembic.
revision = "700a389cb5e1"
down_revision = "fbddd9e181d5"
branch_labels = None
depends_on = None


def upgrade():
    create_table(
        "suspended",
        Column("id", Integer, primary_key=True),
        Column("email", String()),
        Column("end_suspension", DateTime()),
    )


def downgrade():
    drop_table("suspended")
