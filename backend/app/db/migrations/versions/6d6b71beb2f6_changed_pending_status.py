"""changed pending status
Revision ID: 6d6b71beb2f6
Revises: 
Create Date: 2022-11-04 07:31:19.328034
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '6d6b71beb2f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('user',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('register_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', name='user_pkey'),
                    sa.UniqueConstraint('email', name='user_email_key')
                    )
    op.create_table('company',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('hidden', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', 'name', name='company_pkey'),
                    sa.UniqueConstraint('id', name='company_id_key'),
                    sa.UniqueConstraint('name', name='company_name_key')
                    )

    op.create_table('invite',
                    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('status',
                              postgresql.ENUM('accepted', 'declined', 'requested', 'pending', name='invitestatus'),
                              autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='invite_company_id_fkey',
                                            ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='invite_user_id_fkey', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('user_id', 'company_id', name='invite_pkey')
                    )
    op.create_table('member',
                    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('is_owner', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('is_staff', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='member_company_id_fkey',
                                            ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='member_user_id_fkey', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('user_id', 'company_id', name='member_pkey')
                    )


def downgrade() -> None:
    op.drop_table('member')
    op.drop_table('invite')
    op.drop_table('user')
    op.drop_table('company')

