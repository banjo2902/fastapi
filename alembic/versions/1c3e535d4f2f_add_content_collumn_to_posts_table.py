"""add content collumn to posts table

Revision ID: 1c3e535d4f2f
Revises: f6caff4a46bf
Create Date: 2022-08-22 12:25:12.969492

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c3e535d4f2f'
down_revision = 'f6caff4a46bf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("posts", "content")
    pass
