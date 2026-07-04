"""Add auth_token & token_expires_at to users

Revision ID: 7a2f9c4e1b3d
Revises: 48e4a811ffa1
Create Date: 2026-07-04 12:00:00.000000

Migrasi ADITIF: hanya menambah dua kolom baru ke tabel ``users`` untuk
mendukung autentikasi backend berbasis token sesi (lihat
api/auth_utils.py dan endpoint /api/register, /api/login, /api/logout
pada api/app.py). Tidak menghapus atau mengubah kolom/tabel lain yang
sudah ada pada migrasi awal (48e4a811ffa1).
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7a2f9c4e1b3d"
down_revision = "48e4a811ffa1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("auth_token", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("token_expires_at", sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f("ix_users_auth_token"), ["auth_token"], unique=True)


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_users_auth_token"))
        batch_op.drop_column("token_expires_at")
        batch_op.drop_column("auth_token")
