"""inital models for real this time

Revision ID: 1fa71de717eb
Revises: d8c53d2f0c57
Create Date: 2024-07-23 17:25:29.984055

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fa71de717eb'
down_revision: Union[str, None] = 'd8c53d2f0c57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
