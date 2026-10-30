"""Add unique constraint to article URLs

Revision ID: 397356c2397b
Revises:
Create Date: 2026-10-30 13:37:42.904999
"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "397356c2397b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_articles_url",
        "articles",
        ["url"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_articles_url",
        "articles",
        type_="unique",
    )
