"""initial: create projects and bids tables

Revision ID: 0001
Revises:
Create Date: 2026-08-02 00:00:00

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("external_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("url", sa.String(length=1024), nullable=False),
        sa.Column("seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )
    op.create_index("ix_projects_external_id", "projects", ["external_id"], unique=True)

    op.create_table(
        "bids",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("bid_number", sa.Integer(), nullable=False),
        sa.Column("project_external_id", sa.String(length=64), nullable=False),
        sa.Column("project_title", sa.String(length=512), nullable=False),
        sa.Column("project_url", sa.String(length=1024), nullable=False),
        sa.Column("bid_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("delivery_days", sa.Integer(), nullable=False),
        sa.Column("proposal_text", sa.Text(), nullable=False),
        sa.Column("freelancer_bid_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bid_number"),
    )
    op.create_index("ix_bids_bid_number", "bids", ["bid_number"], unique=True)
    op.create_index("ix_bids_project_external_id", "bids", ["project_external_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_bids_project_external_id", table_name="bids")
    op.drop_index("ix_bids_bid_number", table_name="bids")
    op.drop_table("bids")

    op.drop_index("ix_projects_external_id", table_name="projects")
    op.drop_table("projects")
