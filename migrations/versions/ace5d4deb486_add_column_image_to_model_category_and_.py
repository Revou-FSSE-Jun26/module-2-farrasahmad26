"""add column image to model Category and to_dict in Category

Revision ID: ace5d4deb486
Revises: 1b3c87481598
Create Date: 2026-10-27 19:58:56.654589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ace5d4deb486'
down_revision = '1b3c87481598'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_column('image')
