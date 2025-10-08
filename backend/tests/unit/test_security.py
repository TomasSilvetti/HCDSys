import pytest
from datetime import datetime, timedelta
from jose import jwt

from app.utils.security import (
    create_access_token,
    verify_password,
    get_password_hash
)
from app.utils.config import settings

@pytest.mark.unit
class TestSecurity:
    def test_password_hashing(self):
        """Prueba que el hash de contraseña funciona correctamente"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Verificar que el hash no es igual a la contraseña original
        assert hashed != password
        
        # Verificar que la verificación funciona correctamente
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self):
        """Prueba la creación de tokens de acceso"""
        data = {"sub": "test@example.com", "role": "admin"}
        token = create_access_token(data)
        
        # Verificar que el token es una cadena
        assert isinstance(token, str)
        
        # Decodificar el token y verificar los datos
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        assert payload["sub"] == "test@example.com"
        assert payload["role"] == "admin"
        
        # Verificar que el token tiene una fecha de expiración
        assert "exp" in payload
    
    def test_token_expiration(self):
        """Prueba que los tokens expiran correctamente"""
        # Crear un token que expira en 1 segundo
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(seconds=1)
        token = create_access_token(data, expires_delta=expires_delta)
        
        # Verificar que el token es válido inicialmente
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        assert payload["sub"] == "test@example.com"
        
        # Esperar a que expire
        import time
        time.sleep(2)
        
        # Verificar que el token ha expirado
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
