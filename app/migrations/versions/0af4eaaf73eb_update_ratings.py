"""Update ratings

Revision ID: 0af4eaaf73eb
Revises: 8a3bd2ef901c
Create Date: 2024-12-19 13:08:42.660800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0af4eaaf73eb'
down_revision: Union[str, None] = '8a3bd2ef901c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
