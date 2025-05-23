"""Add mango ordering features

Revision ID: d0a9b611a8da
Revises: 938e2b5bb833
Create Date: 2025-05-20 12:12:51.723220

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0a9b611a8da'
down_revision: Union[str, None] = '938e2b5bb833'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_items', sa.Column('unit_price', sa.Float(), nullable=False))
    op.add_column('order_items', sa.Column('total_price', sa.Float(), nullable=False))
    op.add_column('order_items', sa.Column('mango_type', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('order_items', 'mango_type')
    op.drop_column('order_items', 'total_price')
    op.drop_column('order_items', 'unit_price')
    # ### end Alembic commands ###
