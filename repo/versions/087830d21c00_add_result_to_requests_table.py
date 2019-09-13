"""Add Result to Requests table

Revision ID: 087830d21c00
Revises: 700a389cb5e1
Create Date: 2019-08-28 15:23:19.645237

"""
from alembic.op import create_table, drop_table  # type: ignore
from sqlalchemy import Column, String  # type: ignore


# revision identifiers, used by Alembic.
revision = "087830d21c00"
down_revision = "700a389cb5e1"
branch_labels = None
depends_on = None


def upgrade():
    create_table(
        "request_results",
        Column("id_request", String(), primary_key=True),
        Column("status", String()),
        Column("result", String(), server_default="{}"),
    )


def downgrade():
    drop_table("request_results")
