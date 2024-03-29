"""remove duration from script_actions

Revision ID: e5bcd083edb3
Revises: e59dd02c05aa
Create Date: 2023-06-09 23:49:15.729716

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e5bcd083edb3'
down_revision = 'e59dd02c05aa'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('script_actions', 'duration')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('script_actions', sa.Column('duration', mysql.DATETIME(), nullable=True))
    # ### end Alembic commands ###
