"""Add min_stock column to products table

Revision ID: add_min_stock_column
Revises: 
Create Date: 2023-11-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_min_stock_column'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add min_stock column to products table with default value 5
    op.add_column('products', sa.Column('min_stock', sa.Integer(), nullable=True, server_default='5'))


def downgrade():
    # Remove min_stock column from products table
    op.drop_column('products', 'min_stock')