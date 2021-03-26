"""empty message

Revision ID: 20210315_194929
Revises: 20210315_194510
Create Date: 2021-03-15 19:49:29.343136

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20210315_194929'
down_revision = '20210315_194510'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('etl_job_results')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('etl_job_results',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('deleted', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('inserted', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.Column('errors', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('error_summary', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('warning', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('execute_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='etl_job_results_pkey')
    )
    # ### end Alembic commands ###