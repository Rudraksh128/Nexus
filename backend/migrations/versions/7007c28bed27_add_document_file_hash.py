"""add document file hash

Revision ID: 7007c28bed27
Revises: 7c168294b681
Create Date: 2026-09-05

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7007c28bed27"
down_revision: Union[str, Sequence[str], None] = "7c168294b681"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add the column temporarily as nullable so existing rows survive.
    op.add_column(
        "documents",
        sa.Column(
            "file_hash",
            sa.String(length=64),
            nullable=True,
        ),
    )

    # 2. Populate the hash for the existing test document.
    op.execute(
        """
        UPDATE documents
        SET file_hash = '20071C8D005C25BA20DA02CDA9421976A0925C880FE3388840F202F02089D341'
        WHERE id = '5d5e1c89-8483-4c84-985e-dd0dc64779d5'
        """
    )

    # 3. Make the column mandatory.
    op.alter_column(
        "documents",
        "file_hash",
        existing_type=sa.String(length=64),
        nullable=False,
    )

    # 4. Prevent duplicate files.
    op.create_index(
        "ix_documents_file_hash",
        "documents",
        ["file_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_documents_file_hash",
        table_name="documents",
    )

    op.drop_column(
        "documents",
        "file_hash",
    )