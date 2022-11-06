"""Quiz_question_answer
Revision ID: fd07536993e1
Revises: 6d6b71beb2f6
Create Date: 2022-11-05 16:32:57.366250
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = 'fd07536993e1'
down_revision = '6d6b71beb2f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('quiz',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('quiz_id_seq'::regclass)"),
                              autoincrement=True, nullable=False),
                    sa.Column('company_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('description', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('passed_per_day', sa.INTEGER(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['company_id'], ['company.id'], name='quiz_company_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', 'company_id', name='quiz_pkey'),
                    sa.UniqueConstraint('id', name='quiz_id_key'),
                    postgresql_ignore_search_path=False
                    )
    op.create_table('question',
                    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('question_id_seq'::regclass)"),
                              autoincrement=True, nullable=False),
                    sa.Column('quiz_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['quiz_id'], ['quiz.id'], name='question_quiz_id_fkey', ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', 'quiz_id', name='question_pkey'),
                    sa.UniqueConstraint('id', name='question_id_key'),
                    postgresql_ignore_search_path=False
                    )

    op.create_table('answer',
                    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
                    sa.Column('question_id', sa.INTEGER(), autoincrement=False, nullable=False),
                    sa.Column('answer', sa.VARCHAR(), autoincrement=False, nullable=True),
                    sa.Column('is_right', sa.BOOLEAN(), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['question_id'], ['question.id'], name='answer_question_id_fkey',
                                            ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id', 'question_id', name='answer_pkey'),
                    sa.UniqueConstraint('id', name='answer_id_key')
                    )


def downgrade() -> None:
    op.drop_table('answer')
    op.drop_table('question')
    op.drop_table('quiz')
