"""
Add response column to request_metrics table

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20250922_add_response_column"
down_revision = "001_initial_migration"  # Correctly points to initial migration
branch_labels = None
depends_on = None


def upgrade():
    """Add response column to request_metrics table."""
    op.add_column("request_metrics", sa.Column("response", sa.Text(), nullable=True))


def downgrade():
    """Remove response column from request_metrics table."""
    op.drop_column("request_metrics", "response")
