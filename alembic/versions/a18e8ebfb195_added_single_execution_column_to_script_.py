"""added single_execution column to script table

Revision ID: a18e8ebfb195
Revises: 36350102df59
Create Date: 2023-06-17 17:45:00.099779

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a18e8ebfb195'
down_revision = '36350102df59'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scripts', sa.Column('single_execution', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('scripts', 'single_execution')
    # ### end Alembic commands ###