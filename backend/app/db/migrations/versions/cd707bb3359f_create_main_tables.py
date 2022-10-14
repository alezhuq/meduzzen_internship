"""create_main_tables
Revision ID: cd707bb3359f
Revises: 04c303fd2633
Create Date: 2022-10-14 16:12:52.528389
"""
import datetime
import sqlalchemy as sa
from alembic import op
# revision identifiers, used by Alembic
revision = 'cd707bb3359f'
down_revision = '04c303fd2633'
branch_labels = None
depends_on = None


def create_users_table() -> None:
    op.create_table(
        'Users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, unique=True),
        sa.Column('username', sa.String),
        sa.Column('email', sa.String, primary_key=True, unique=True),
        sa.Column('password', sa.String, primary_key=True),
        sa.Column('register_date', sa.DateTime, default=datetime.datetime.utcnow),
        sa.Column('is_active', sa.Boolean),
    )


def upgrade() -> None:
    create_users_table()


def downgrade() -> None:
    op.drop_table("Users")
