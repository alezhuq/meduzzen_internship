import sqlalchemy as sa
import datetime

Users = sa.Table(
    'Users',
    sa.MetaData(),
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True, unique=True),
    sa.Column('username', sa.String),
    sa.Column('email', sa.String, primary_key=True, unique=True),
    sa.Column('password', sa.String, primary_key=True),
    sa.Column('register_date', sa.DateTime, default=datetime.datetime.utcnow),
    sa.Column('is_active', sa.Boolean),
)