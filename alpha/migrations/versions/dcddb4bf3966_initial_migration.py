"""Initial migration

Revision ID: dcddb4bf3966
Revises: 
Create Date: 2024-08-23 15:30:06.621342

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dcddb4bf3966'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quest', schema=None) as batch_op:
        batch_op.alter_column('reward',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=False)
        batch_op.alter_column('rarity',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               nullable=True)

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('solde',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               existing_nullable=True,
               existing_server_default=sa.text('0'))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('solde',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=True,
               existing_server_default=sa.text('0'))

    with op.batch_alter_table('quest', schema=None) as batch_op:
        batch_op.alter_column('rarity',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('reward',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###