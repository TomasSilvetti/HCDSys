import pytest
import io
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Usuario as User, Documento as Document, VersionDocumento as DocumentVersion
from app.utils.security import get_password_hash

@pytest.mark.integration
@pytest.mark.asyncio
class TestDocumentFlow:
    async def test_document_creation_and_retrieval(self, async_client: AsyncClient, db_session: AsyncSession):
        """Prueba el flujo de creación y recuperación de documentos"""
        # 1. Crear un usuario gestor para las pruebas
        test_user = User(
            email="gestor_doc@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Gestor Documentos",
            role_name="gestor"
        )
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)
        
        # 2. Iniciar sesión con el usuario
        login_data = {
            "email": "gestor_doc@example.com",
            "password": "password123"
        }
        
        login_response = await async_client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Crear un nuevo documento
        # Simular un archivo para subir
        file_content = b"Contenido de prueba del documento"
        file = io.BytesIO(file_content)
        
        # Datos del formulario
        form_data = {
            "title": "Documento de Prueba",
            "description": "Este es un documento de prueba para integración",
            "document_type": "informe"
        }
        
        files = {
            "file": ("test_document.pdf", file, "application/pdf")
        }
        
        # Enviar solicitud para crear documento
        response = await async_client.post(
            "/documents/",
            headers=headers,
            data=form_data,
            files=files
        )
        
        # Verificar respuesta
        assert response.status_code == 201
        document_data = response.json()
        assert document_data["title"] == "Documento de Prueba"
        assert document_data["description"] == "Este es un documento de prueba para integración"
        assert "id" in document_data
        
        # 4. Obtener el documento creado
        document_id = document_data["id"]
        response = await async_client.get(f"/documents/{document_id}", headers=headers)
        
        # Verificar respuesta
        assert response.status_code == 200
        retrieved_document = response.json()
        assert retrieved_document["id"] == document_id
        assert retrieved_document["title"] == "Documento de Prueba"
        
        # 5. Listar todos los documentos
        response = await async_client.get("/documents/", headers=headers)
        
        # Verificar respuesta
        assert response.status_code == 200
        documents_list = response.json()
        assert isinstance(documents_list, list)
        assert len(documents_list) >= 1
        
        # Verificar que el documento creado está en la lista
        document_ids = [doc["id"] for doc in documents_list]
        assert document_id in document_ids
    
    async def test_document_update_and_versioning(self, async_client: AsyncClient, db_session: AsyncSession):
        """Prueba el flujo de actualización y versionado de documentos"""
        # 1. Crear un usuario gestor para las pruebas
        test_user = User(
            email="gestor_version@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Gestor Versiones",
            role_name="gestor"
        )
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)
        
        # 2. Iniciar sesión con el usuario
        login_data = {
            "email": "gestor_version@example.com",
            "password": "password123"
        }
        
        login_response = await async_client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Crear un documento inicial
        file_content = b"Contenido inicial del documento"
        file = io.BytesIO(file_content)
        
        form_data = {
            "title": "Documento para Versionar",
            "description": "Este documento será versionado",
            "document_type": "informe"
        }
        
        files = {
            "file": ("version_doc.pdf", file, "application/pdf")
        }
        
        response = await async_client.post(
            "/documents/",
            headers=headers,
            data=form_data,
            files=files
        )
        
        document_id = response.json()["id"]
        
        # 4. Actualizar el documento (crear nueva versión)
        updated_file_content = b"Contenido actualizado del documento"
        updated_file = io.BytesIO(updated_file_content)
        
        version_form_data = {
            "comentario": "Actualización de prueba",
            "cambios": "Se actualizó el contenido del documento"
        }
        
        version_files = {
            "file": ("version_doc_v2.pdf", updated_file, "application/pdf")
        }
        
        response = await async_client.post(
            f"/documents/{document_id}/versions",
            headers=headers,
            data=version_form_data,
            files=version_files
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        version_data = response.json()
        assert "version_id" in version_data
        
        # 5. Obtener historial de versiones
        response = await async_client.get(
            f"/documents/{document_id}/versions",
            headers=headers
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        versions = response.json()
        assert isinstance(versions, list)
        assert len(versions) == 2  # Versión inicial + actualización
        
        # Verificar que las versiones están ordenadas correctamente
        assert versions[0]["numero_version"] > versions[1]["numero_version"]
        
        # 6. Verificar que la versión actual es la más reciente
        response = await async_client.get(f"/documents/{document_id}", headers=headers)
        document = response.json()
        
        # La versión actual debe ser la 2
        assert document["current_version"] == 2
    
    async def test_document_search_and_filtering(self, async_client: AsyncClient, db_session: AsyncSession):
        """Prueba el flujo de búsqueda y filtrado de documentos"""
        # 1. Crear un usuario para las pruebas
        test_user = User(
            email="search_user@example.com",
            hashed_password=get_password_hash("password123"),
            full_name="Usuario Búsqueda",
            role_name="usuario"
        )
        db_session.add(test_user)
        await db_session.commit()
        await db_session.refresh(test_user)
        
        # 2. Iniciar sesión con el usuario
        login_data = {
            "email": "search_user@example.com",
            "password": "password123"
        }
        
        login_response = await async_client.post("/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Crear varios documentos con diferentes características
        # Documento 1: Informe técnico
        doc1_content = b"Este es un informe tecnico sobre sistemas informaticos"
        doc1_file = io.BytesIO(doc1_content)
        
        doc1_data = {
            "title": "Informe Técnico Sistemas",
            "description": "Informe detallado sobre sistemas informáticos",
            "document_type": "informe",
            "tags": "técnico,sistemas,informática"
        }
        
        doc1_files = {
            "file": ("informe_tecnico.pdf", doc1_file, "application/pdf")
        }
        
        await async_client.post(
            "/documents/",
            headers=headers,
            data=doc1_data,
            files=doc1_files
        )
        
        # Documento 2: Manual de usuario
        doc2_content = b"Este es un manual de usuario para el sistema XYZ"
        doc2_file = io.BytesIO(doc2_content)
        
        doc2_data = {
            "title": "Manual de Usuario XYZ",
            "description": "Manual para usuarios del sistema XYZ",
            "document_type": "manual",
            "tags": "manual,usuario,xyz"
        }
        
        doc2_files = {
            "file": ("manual_usuario.docx", doc2_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        
        await async_client.post(
            "/documents/",
            headers=headers,
            data=doc2_data,
            files=doc2_files
        )
        
        # 4. Realizar búsqueda por término
        response = await async_client.get(
            "/documents/search?q=manual",
            headers=headers
        )
        
        # Verificar resultados
        assert response.status_code == 200
        search_results = response.json()
        assert "results" in search_results
        assert len(search_results["results"]) == 1
        assert search_results["results"][0]["title"] == "Manual de Usuario XYZ"
        
        # 5. Realizar búsqueda con filtros
        response = await async_client.get(
            "/documents/search?document_type=informe",
            headers=headers
        )
        
        # Verificar resultados
        assert response.status_code == 200
        search_results = response.json()
        assert len(search_results["results"]) == 1
        assert search_results["results"][0]["title"] == "Informe Técnico Sistemas"
        
        # 6. Búsqueda por etiquetas
        response = await async_client.get(
            "/documents/search?tags=técnico",
            headers=headers
        )
        
        # Verificar resultados
        assert response.status_code == 200
        search_results = response.json()
        assert len(search_results["results"]) == 1
        assert search_results["results"][0]["title"] == "Informe Técnico Sistemas"
