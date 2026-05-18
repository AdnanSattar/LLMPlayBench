"""Initial migration - create request_metrics table

Revision ID: 001_initial_migration
Revises:
Create Date: 2025-09-18

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "001_initial_migration"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create request_metrics table
    op.create_table(
        "request_metrics",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("request_id", sa.String(), index=True, unique=True),
        sa.Column(
            "timestamp", sa.Integer(), default=sa.text("extract(epoch from now())")
        ),
        sa.Column("model", sa.String(), index=True),
        sa.Column("prompt", sa.Text()),
        sa.Column("prompt_length", sa.Integer()),
        sa.Column("latency_s", sa.Float()),
        sa.Column("tokens", sa.Integer()),
        sa.Column("tokens_per_sec", sa.Float()),
        sa.Column("quantization", sa.String()),
    )


def downgrade() -> None:
    # Drop request_metrics table
    op.drop_table("request_metrics")
