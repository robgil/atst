"""add Environment creator_role

Revision ID: cfab6c8243cb
Revises: 502e79c55d2d
Create Date: 2019-09-10 11:21:43.252592

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cfab6c8243cb' # pragma: allowlist secret
down_revision = '502e79c55d2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('environments', sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False))
    op.create_foreign_key("fk_users_id", 'environments', 'users', ['creator_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("fk_users_id", 'environments', type_='foreignkey')
    op.drop_column('environments', 'creator_id')
    # ### end Alembic commands ###