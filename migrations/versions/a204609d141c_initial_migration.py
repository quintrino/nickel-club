"""Initial migration

Revision ID: a204609d141c
Revises: 
Create Date: 2022-04-04 15:08:24.326978

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a204609d141c"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "admin_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("password", sa.String(length=200), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "club_member",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("nickels", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "nickel_request",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "request_type",
            sa.Enum("debit", "credit", name="nickelrequesttype"),
            nullable=False,
        ),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("reason", sa.UnicodeText(), nullable=True),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["member_id"],
            ["club_member.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("nickel_request")
    op.drop_table("club_member")
    op.drop_table("admin_user")
    # ### end Alembic commands ###
