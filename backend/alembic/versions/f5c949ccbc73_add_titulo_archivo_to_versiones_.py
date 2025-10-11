"""add_titulo_archivo_to_versiones_documento

Revision ID: f5c949ccbc73
Revises: 422d0737a597
Create Date: 2025-10-11 11:25:57.719401

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5c949ccbc73'
down_revision = '422d0737a597'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('versiones_documento', sa.Column('titulo_archivo', sa.String(), nullable=True))
    
    # Actualizar los registros existentes para usar el título del documento como valor inicial
    op.execute("""
        UPDATE versiones_documento vd
        SET titulo_archivo = d.titulo
        FROM documentos d
        WHERE vd.documento_id = d.id
    """)


def downgrade() -> None:
    op.drop_column('versiones_documento', 'titulo_archivo')
