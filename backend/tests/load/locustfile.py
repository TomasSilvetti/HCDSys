"""
Archivo de configuración para pruebas de carga con Locust
"""
import os
import random
import json
import time
from pathlib import Path
from locust import HttpUser, task, between
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Constantes
BASE_URL = os.getenv("LOAD_TEST_BASE_URL", "http://localhost:8000")
TEST_USER_EMAIL = os.getenv("TEST_USER_EMAIL", "test@example.com")
TEST_USER_PASSWORD = os.getenv("TEST_USER_PASSWORD", "password123")

# Datos de prueba
SAMPLE_DOCUMENT = {
    "title": "Documento de prueba",
    "description": "Este es un documento de prueba para las pruebas de carga",
    "category": "ORDENANZA",
    "tags": ["prueba", "carga", "rendimiento"]
}

class DocumentAPIUser(HttpUser):
    """
    Usuario simulado para pruebas de carga de la API de documentos
    """
    wait_time = between(1, 5)  # Tiempo de espera entre tareas en segundos
    token = None
    document_ids = []
    
    def on_start(self):
        """
        Método que se ejecuta cuando un usuario comienza la simulación
        """
        # Autenticación
        response = self.client.post(
            "/api/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
            
            # Obtener algunos IDs de documentos para las pruebas
            docs_response = self.client.get("/api/documents")
            if docs_response.status_code == 200:
                documents = docs_response.json()
                self.document_ids = [doc["id"] for doc in documents[:10]]
    
    @task(3)
    def get_documents_list(self):
        """
        Tarea para obtener la lista de documentos
        """
        self.client.get("/api/documents")
    
    @task(2)
    def search_documents(self):
        """
        Tarea para buscar documentos
        """
        search_terms = ["prueba", "documento", "ordenanza", "resolución", ""]
        term = random.choice(search_terms)
        self.client.get(f"/api/documents?search={term}")
    
    @task(1)
    def get_document_detail(self):
        """
        Tarea para obtener el detalle de un documento
        """
        if self.document_ids:
            doc_id = random.choice(self.document_ids)
            self.client.get(f"/api/documents/{doc_id}")
    
    @task(1)
    def create_document(self):
        """
        Tarea para crear un nuevo documento
        """
        doc = SAMPLE_DOCUMENT.copy()
        doc["title"] = f"Documento de prueba {int(time.time())}"
        response = self.client.post("/api/documents", json=doc)
        if response.status_code == 201:
            new_doc_id = response.json().get("id")
            if new_doc_id:
                self.document_ids.append(new_doc_id)
    
    @task(1)
    def update_document(self):
        """
        Tarea para actualizar un documento existente
        """
        if self.document_ids:
            doc_id = random.choice(self.document_ids)
            self.client.put(
                f"/api/documents/{doc_id}",
                json={"title": f"Documento actualizado {int(time.time())}"}
            )

class UserAPIUser(HttpUser):
    """
    Usuario simulado para pruebas de carga de la API de usuarios
    """
    wait_time = between(2, 5)  # Tiempo de espera entre tareas en segundos
    token = None
    
    def on_start(self):
        """
        Método que se ejecuta cuando un usuario comienza la simulación
        """
        # Autenticación como administrador
        response = self.client.post(
            "/api/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.client.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_users_list(self):
        """
        Tarea para obtener la lista de usuarios
        """
        self.client.get("/api/users")
    
    @task(2)
    def get_roles_list(self):
        """
        Tarea para obtener la lista de roles
        """
        self.client.get("/api/roles")
    
    @task(1)
    def get_permissions_list(self):
        """
        Tarea para obtener la lista de permisos
        """
        self.client.get("/api/permissions")

class AnonymousUser(HttpUser):
    """
    Usuario anónimo para simular tráfico sin autenticación
    """
    wait_time = between(1, 3)  # Tiempo de espera entre tareas en segundos
    
    @task(5)
    def visit_health_check(self):
        """
        Tarea para verificar el estado de la API
        """
        self.client.get("/api/health")
    
    @task(2)
    def failed_login_attempt(self):
        """
        Tarea para simular intentos de inicio de sesión fallidos
        """
        self.client.post(
            "/api/auth/login",
            json={"email": f"fake{random.randint(1, 1000)}@example.com", "password": "wrongpassword"}
        )
