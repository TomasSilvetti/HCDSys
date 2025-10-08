"""
Mocks para el sistema de almacenamiento
"""
from unittest.mock import AsyncMock, MagicMock
import os
from typing import Dict, Any, Optional

# Mock para el sistema de almacenamiento de archivos
class MockStorage:
    def __init__(self):
        self.saved_files = {}
        
    async def save_file(self, file_content, directory: str, filename: str) -> str:
        """Mock para guardar un archivo"""
        path = os.path.join(directory, filename)
        self.saved_files[path] = file_content
        return path
        
    async def get_file(self, file_path: str) -> bytes:
        """Mock para obtener un archivo"""
        if file_path in self.saved_files:
            return self.saved_files[file_path]
        raise FileNotFoundError(f"File not found: {file_path}")
        
    async def delete_file(self, file_path: str) -> bool:
        """Mock para eliminar un archivo"""
        if file_path in self.saved_files:
            del self.saved_files[file_path]
            return True
        return False
        
    async def file_exists(self, file_path: str) -> bool:
        """Mock para verificar si un archivo existe"""
        return file_path in self.saved_files

# Mock para el servicio de almacenamiento
def create_mock_storage_service():
    service = MagicMock()
    service.save_file = AsyncMock(return_value="mocked/path/file.pdf")
    service.get_file = AsyncMock(return_value=b"mocked file content")
    service.delete_file = AsyncMock(return_value=True)
    service.file_exists = AsyncMock(return_value=True)
    return service
