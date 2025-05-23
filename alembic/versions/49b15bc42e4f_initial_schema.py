"""initial schema

Revision ID: 49b15bc42e4f
Revises: 
Create Date: 2025-05-14 02:16:24.892164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49b15bc42e4f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'is_featured')
    op.drop_column('products', 'is_active')
    op.drop_column('products', 'stock')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('stock', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('products', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('products', sa.Column('is_featured', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
