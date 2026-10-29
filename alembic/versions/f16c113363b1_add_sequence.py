"""add sequence

Revision ID: f16c113363b1
Revises: fd447f5ddbbb
Create Date: 2026-07-26 15:31:31.798563

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f16c113363b1"
down_revision: Union[str, Sequence[str], None] = "fd447f5ddbbb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS global_id_seq "
        "START WITH 10000 INCREMENT BY 1"
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        "DROP SEQUENCE IF EXISTS global_id_seq"
    )