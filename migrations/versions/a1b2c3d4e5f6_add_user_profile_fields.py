"""add user profile fields

Revision ID: a1b2c3d4e5f6
Revises: 9c2f8d2a1a6e
"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '9c2f8d2a1a6e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('profile_photo_path', sa.String(length=500), nullable=True))
    op.add_column('users', sa.Column('medical_conditions', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('users', 'medical_conditions')
    op.drop_column('users', 'profile_photo_path')
