from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..utils.security import get_current_user_ws
from ..db import models

router = APIRouter()

# Clase para gestionar las conexiones WebSocket
class ConnectionManager:
    def __init__(self):
        # Conexiones activas: {usuario_id: {conexión1, conexión2, ...}}
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Conexiones por rol: {rol_id: {usuario_id1, usuario_id2, ...}}
        self.role_connections: Dict[int, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, role_id: int):
        await websocket.accept()
        
        # Añadir a conexiones activas
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Añadir a conexiones por rol
        if role_id not in self.role_connections:
            self.role_connections[role_id] = set()
        self.role_connections[role_id].add(user_id)
    
    def disconnect(self, websocket: WebSocket, user_id: int, role_id: int):
        # Eliminar de conexiones activas
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
                # Eliminar de conexiones por rol
                if role_id in self.role_connections:
                    self.role_connections[role_id].discard(user_id)
                    if not self.role_connections[role_id]:
                        del self.role_connections[role_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)
    
    async def broadcast_to_role(self, message: dict, role_id: int):
        if role_id in self.role_connections:
            for user_id in self.role_connections[role_id]:
                await self.send_personal_message(message, user_id)
    
    async def broadcast(self, message: dict):
        for user_id in self.active_connections:
            await self.send_personal_message(message, user_id)

# Instancia del gestor de conexiones
manager = ConnectionManager()

# WebSocket para actualizaciones en tiempo real
@router.websocket("/ws/permissions")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    try:
        # Autenticar usuario
        user = await get_current_user_ws(token, db)
        
        # Conectar WebSocket
        await manager.connect(websocket, user.id, user.role_id)
        
        try:
            while True:
                # Esperar mensajes del cliente
                data = await websocket.receive_text()
                
                # Aquí podríamos procesar mensajes específicos del cliente
                # Por ahora, solo enviamos un eco
                await manager.send_personal_message(
                    {"action": "echo", "message": data},
                    user.id
                )
        except WebSocketDisconnect:
            # Desconectar cuando el cliente cierra la conexión
            manager.disconnect(websocket, user.id, user.role_id)
    except HTTPException:
        # En caso de error de autenticación
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    except Exception as e:
        # En caso de otros errores
        print(f"WebSocket error: {str(e)}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

# Función para notificar cambios de permisos
async def notify_permission_change(role_id: int, permission_id: int, action: str, db: Session):
    """
    Notifica a los usuarios afectados sobre cambios en permisos.
    """
    try:
        # Obtener información del permiso
        permission = db.query(models.Permiso).filter(models.Permiso.id == permission_id).first()
        
        if not permission:
            print(f"Error: Permiso con ID {permission_id} no encontrado")
            return
        
        # Construir mensaje
        message = {
            "action": "permission_change",
            "permission_id": permission_id,
            "permission_name": permission.nombre,
            "permission_code": permission.codigo,
            "role_id": role_id,
            "change_action": action
        }
        
        # Enviar notificación a todos los usuarios del rol afectado
        await manager.broadcast_to_role(message, role_id)
        
    except Exception as e:
        print(f"Error al notificar cambio de permiso: {str(e)}")
