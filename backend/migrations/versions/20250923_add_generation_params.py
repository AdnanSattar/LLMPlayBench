"""
Add generation parameters columns to request_metrics table

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20250923_add_generation_params"
down_revision = "20250922_add_response_column"  # Points to previous migration
branch_labels = None
depends_on = None


def upgrade():
    """Add generation parameters columns to request_metrics table."""
    op.add_column(
        "request_metrics", sa.Column("temperature", sa.Float(), nullable=True)
    )
    op.add_column("request_metrics", sa.Column("top_p", sa.Float(), nullable=True))
    op.add_column("request_metrics", sa.Column("top_k", sa.Integer(), nullable=True))
    op.add_column(
        "request_metrics", sa.Column("system_prompt", sa.Text(), nullable=True)
    )


def downgrade():
    """Remove generation parameters columns from request_metrics table."""
    op.drop_column("request_metrics", "system_prompt")
    op.drop_column("request_metrics", "top_k")
    op.drop_column("request_metrics", "top_p")
    op.drop_column("request_metrics", "temperature")
