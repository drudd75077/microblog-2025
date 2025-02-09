"""about me and last seen user model

Revision ID: 128c80ef11dc
Revises: ba3cd7c7241b
Create Date: 2025-01-30 23:38:20.205644

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '128c80ef11dc'
down_revision = 'ba3cd7c7241b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('about_me', sa.String(length=140), nullable=True))
        batch_op.add_column(sa.Column('last_seen', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('last_seen')
        batch_op.drop_column('about_me')

    # ### end Alembic commands ###
