"""update_user/refresh true

Revision ID: a83cb435bf75
Revises: c00e09bf5b2b
Create Date: 2024-12-21 16:40:12.414681

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a83cb435bf75'
down_revision: Union[str, None] = 'c00e09bf5b2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'refresh_token',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'refresh_token',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
