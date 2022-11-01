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
    op.create_table('User',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"User_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('password', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('register_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
                    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', 'email', 'password', name='User_pkey'),
                    sa.UniqueConstraint('email', name='User_email_key'),
                    sa.UniqueConstraint('id', name='User_id_key'),
                    postgresql_ignore_search_path=False
                    )
    op.create_table('Company',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"Company_id_seq"\'::regclass)'),
                              autoincrement=True, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
                    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
                    sa.Column('hidden', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.PrimaryKeyConstraint('id', 'name', name='Company_pkey'),
                    sa.UniqueConstraint('id', name='Company_id_key'),
                    sa.UniqueConstraint('name', name='Company_name_key')
                    )
    op.create_table('Invite',
                    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('pending_status', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['company_id'], ['Company.id'], name='Invite_company_id_fkey',
                                            ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['user_id'], ['User.id'], name='Invite_user_id_fkey', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('user_id', 'company_id', name='Invite_pkey')
                    )
    op.create_table('UserInCompany',
                    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('is_owner', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.Column('is_staff', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['company_id'], ['Company.id'], name='UserInCompany_company_id_fkey',
                                            ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['user_id'], ['User.id'], name='UserInCompany_user_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('user_id', 'company_id', name='UserInCompany_pkey')
                    )


def downgrade() -> None:
    op.drop_table('UserInCompany')
    op.drop_table('Invite')
    op.drop_table('User')
    op.drop_table('Company')
