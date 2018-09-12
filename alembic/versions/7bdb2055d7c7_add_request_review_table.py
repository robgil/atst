"""add request review table

Revision ID: 7bdb2055d7c7
Revises: ad30159ef19b
Create Date: 2018-09-06 15:15:40.666840

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '7bdb2055d7c7'
down_revision = 'ad30159ef19b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('request_reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('comments', sa.String(), nullable=True),
    sa.Column('fname_mao', sa.String(), nullable=True),
    sa.Column('lname_mao', sa.String(), nullable=True),
    sa.Column('email_mao', sa.String(), nullable=True),
    sa.Column('phone_mao', sa.String(), nullable=True),
    sa.Column('fname_ccpo', sa.String(), nullable=True),
    sa.Column('lname_ccpo', sa.String(), nullable=True),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('request_status_events', sa.Column('request_review_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'request_status_events', 'request_reviews', ['request_review_id'], ['id'])
    op.create_foreign_key(None, 'request_reviews', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'request_status_events', type_='foreignkey')
    op.drop_constraint(None, 'request_reviews', type_='foreignkey')
    op.drop_column('request_status_events', 'request_review_id')
    op.drop_table('request_reviews')
    # ### end Alembic commands ###