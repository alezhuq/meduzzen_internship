"""added_companies_and_invites
Revision ID: a61a72247a97
Revises: cd707bb3359f
Create Date: 2022-10-28 09:41:05.190508
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'a61a72247a97'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('user',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"user_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('register_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', 'email', 'password', name='user_pkey'),
                    sa.UniqueConstraint('email', name='user_email_key'),
                    sa.UniqueConstraint('id', name='user_id_key'),
                    postgresql_ignore_search_path=False
                    )
    op.create_table('company',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"company_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
                    sa.Column('hidden', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', 'name', name='company_pkey'),
                    sa.UniqueConstraint('id', name='company_id_key'),
                    sa.UniqueConstraint('name', name='company_name_key')
                    )
    op.create_table('invite',
                    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('pending_status', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='invitec_company_id_fkey',
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
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='member_user_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('user_id', 'company_id', name='member_pkey')
                    )


def downgrade() -> None:
    op.drop_table('UserInCompany')
    op.drop_table('Invite')
    op.drop_table('User')
    op.drop_table('Company')
