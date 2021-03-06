"""empty message

Revision ID: 20210120_074454
Revises: 20210111_220218
Create Date: 2021-01-20 07:44:54.234082

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20210120_074454"
down_revision = "20210111_220218"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_items_description"), "items", ["description"], unique=False
    )
    op.create_index(op.f("ix_items_title"), "items", ["title"], unique=False)
    op.add_column("users", sa.Column("disabled", sa.Boolean(), nullable=True))
    op.add_column("users", sa.Column("email", sa.String(), nullable=True))
    op.add_column("users", sa.Column("full_name", sa.String(), nullable=True))
    op.add_column("users", sa.Column("hashed_password", sa.String(), nullable=True))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.add_column("users", sa.Column("is_test", sa.Boolean(), nullable=True))
    op.add_column("users", sa.Column("username", sa.String(), nullable=True))
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    op.drop_index("ix_users_id", table_name="users")
    op.drop_column("users", "name")
    op.drop_column("users", "age")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users", sa.Column("age", sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "users", sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.create_index("ix_users_id", "users", ["id"], unique=False)
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_column("users", "username")
    op.drop_column("users", "is_test")
    op.drop_column("users", "is_active")
    op.drop_column("users", "hashed_password")
    op.drop_column("users", "full_name")
    op.drop_column("users", "email")
    op.drop_column("users", "disabled")
    op.drop_index(op.f("ix_items_title"), table_name="items")
    op.drop_index(op.f("ix_items_description"), table_name="items")
    op.drop_table("items")
    # ### end Alembic commands ###
