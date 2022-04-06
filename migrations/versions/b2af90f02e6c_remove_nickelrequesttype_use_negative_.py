"""Remove NickelRequestType, use negative values instead

Revision ID: b2af90f02e6c
Revises: 39b10ff88b45
Create Date: 2022-04-06 12:54:58.654909

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b2af90f02e6c"
down_revision = "39b10ff88b45"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE nickel_request SET amount = -1 * amount WHERE request_type = 'credit'; "
    )
    op.drop_column("nickel_request", "request_type")
    sa.Enum(name="nickelrequesttype").drop(op.get_bind(), checkfirst=False)


def downgrade():
    # todo: not sure if I need this or add column will automatically create it
    op.execute("CREATE TYPE nickelrequesttype AS ENUM ( 'debit', 'credit' ); ")

    op.add_column(
        "nickel_request",
        sa.Column(
            "request_type",
            postgresql.ENUM("debit", "credit", name="nickelrequesttype"),
            autoincrement=False,
            nullable=True,
        ),
    )

    op.execute("UPDATE nickel_request SET request_type = 'debit' WHERE amount > 0; ")
    op.execute("UPDATE nickel_request SET request_type = 'credit' WHERE amount <= 0; ")
    op.execute("UPDATE nickel_request SET amount = ABS(amount); ")

    op.alter_column("nickel_request", "request_type", nullable=False)
