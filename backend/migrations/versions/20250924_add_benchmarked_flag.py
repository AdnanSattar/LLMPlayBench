"""
Add benchmarked boolean column to request_metrics

Author: Adnan Sattar
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20250924_add_benchmarked_flag"
down_revision = "20250923_add_generation_params"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "request_metrics",
        sa.Column(
            "benchmarked", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
    )
    # create index for faster filters
    op.create_index(
        "ix_request_metrics_benchmarked", "request_metrics", ["benchmarked"]
    )


def downgrade():
    op.drop_index("ix_request_metrics_benchmarked", table_name="request_metrics")
    op.drop_column("request_metrics", "benchmarked")
