# auth.py

import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from db.db import get_conexion

# Configuración de la aplicación
SECRET_KEY = "YOUR_SECRET_KEY"  # Cambia esto por una clave secreta real
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funciones de autenticación
# Función para hashear la contraseña
def hash_password(password: str):
    """Hashea la contraseña usando bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(username: str, password: str):
    # Obtén la conexión a la base de datos
    conn = get_conexion()

    # Ejecuta la consulta y obtén los datos del usuario
    user = conn.execute('SELECT ID, Username, Password, Role FROM Users WHERE Username = ?', (username,)).fetchone()
    
    # Cierra la conexión
    conn.close()

    # Verifica si el usuario no existe o la contraseña no es correcta
    if user is None or not verify_password(password, user[2]):
        return False
    
    # Devuelve los datos del usuario en formato diccionario
    return {
        'id': user[0],  # ID del usuario
        'Username': user[1],  # Nombre de usuario
        'Password': user[2],  # Contraseña (hashed)
        'Role': user[3]  # Rol del usuario
    }


def create_user(username: str, password: str):
    conn = get_conexion()
    
    # Verificar si el usuario ya existe
    user = conn.execute('SELECT * FROM Users WHERE Username = ?', (username,)).fetchone()
    if user:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Insertar un nuevo usuario
    hashed_password = get_password_hash(password)
    conn.execute('INSERT INTO Users (Username, Passsword) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()
