"""add image and slug column on Product table. add category, image, and slug on to_dict function on Product class

Revision ID: 1b3c87481598
Revises: d41a850b6f1f
Create Date: 2026-10-27 13:21:50.468832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1b3c87481598'
down_revision = 'd41a850b6f1f'
branch_labels = None
depends_on = None


def upgrade():
    # Add slug as nullable first so existing rows don't violate NOT NULL.
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('slug', sa.String(length=100), nullable=True))

    # Backfill slugs for existing products from their name, suffixed with the id
    # so they are guaranteed unique (Postgres syntax).
    op.execute("""
        UPDATE products
        SET slug = left(trim(both '-' from regexp_replace(lower(name), '[^a-z0-9]+', '-', 'g')), 90) || '-' || id
        WHERE slug IS NULL
    """)

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('slug', existing_type=sa.String(length=100), nullable=False)
        batch_op.create_unique_constraint('uq_products_slug', ['slug'])


def downgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_constraint('uq_products_slug', type_='unique')
        batch_op.drop_column('slug')
        batch_op.drop_column('image')
