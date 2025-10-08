"""Mejora del sistema de versionado de documentos

Revision ID: ed3cd3bf2865
Revises: 
Create Date: 2025-10-07 23:51:11.693971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed3cd3bf2865'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Añadir nuevas columnas a la tabla versiones_documento
    op.add_column('versiones_documento', sa.Column('version_anterior_id', sa.Integer(), nullable=True))
    op.add_column('versiones_documento', sa.Column('hash_archivo', sa.String(), nullable=True))
    op.add_column('versiones_documento', sa.Column('tamano_archivo', sa.Integer(), nullable=True))
    op.add_column('versiones_documento', sa.Column('extension_archivo', sa.String(), nullable=True))
    op.add_column('versiones_documento', sa.Column('cambios', sa.Text(), nullable=True))
    op.add_column('versiones_documento', sa.Column('es_actual', sa.Boolean(), server_default='false', nullable=False))
    
    # Añadir clave foránea para version_anterior_id
    op.create_foreign_key(
        'fk_version_anterior', 
        'versiones_documento', 
        'versiones_documento', 
        ['version_anterior_id'], 
        ['id']
    )


def downgrade() -> None:
    # Eliminar la clave foránea
    op.drop_constraint('fk_version_anterior', 'versiones_documento', type_='foreignkey')
    
    # Eliminar las columnas añadidas
    op.drop_column('versiones_documento', 'es_actual')
    op.drop_column('versiones_documento', 'cambios')
    op.drop_column('versiones_documento', 'extension_archivo')
    op.drop_column('versiones_documento', 'tamano_archivo')
    op.drop_column('versiones_documento', 'hash_archivo')
    op.drop_column('versiones_documento', 'version_anterior_id')
