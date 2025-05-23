"""add_variation_name_to_product

Revision ID: 8188da137d22
Revises: d0a9b611a8da
Create Date: 2025-05-22 23:55:18.604611

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8188da137d22'
down_revision: Union[str, None] = 'd0a9b611a8da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('variation_name', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'variation_name')
    # ### end Alembic commands ###
