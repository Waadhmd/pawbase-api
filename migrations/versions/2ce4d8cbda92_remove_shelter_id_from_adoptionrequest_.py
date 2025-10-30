"""Remove shelter_id from AdoptionRequest and rename password_hash to password and add role to User"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "2ce4d8cbda92"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Remove shelter_id and its constraint ---
    op.drop_constraint("adoptionrequest_shelter_id_fkey", "adoptionrequest", type_="foreignkey")
    op.drop_column("adoptionrequest", "shelter_id")

    # --- Add 'password' column ---
    op.add_column("user", sa.Column("password", sa.String(), nullable=True))

    # Copy old password_hash data if exists
    op.execute('UPDATE "user" SET password = COALESCE(password_hash, \'temp_password\')')

    # Drop old password_hash
    op.drop_column("user", "password_hash")

    # --- Add 'role' column (enum already exists in DB) ---
    op.add_column(
        "user",
        sa.Column(
            "role",
            sa.Enum("org_admin", "staff", "adopter", name="userrole"),
            nullable=False,
            server_default="adopter",
        ),
    )

    # --- Make password not null ---
    op.alter_column("user", "password", nullable=False)


def downgrade() -> None:
    # Reverse 'role' addition
    op.drop_column("user", "role")

    # Restore old password_hash
    op.add_column("user", sa.Column("password_hash", sa.String(), nullable=False))
    op.execute('UPDATE "user" SET password_hash = password')
    op.drop_column("user", "password")

    # Restore shelter_id
    op.add_column("adoptionrequest", sa.Column("shelter_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "adoptionrequest_shelter_id_fkey", "adoptionrequest", "shelter", ["shelter_id"], ["id"]
    )
