from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime
from jose import JWTError, jwt
from config.auth import create_user, authenticate_user, create_access_token,hash_password
from db.db import get_conexion
from pydantic import BaseModel 
from models.Auth import UserCreate
from typing import Optional, List

# Configuración del token
SECRET_KEY = "YOUR_SECRET_KEY"  # Cambia esto por una clave secreta real
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Define el esquema para la autenticación
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)




@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate):
    # Verifica si el nombre de usuario ya existe en la base de datos
    
    conn = get_conexion()
    existing_user = conn.execute('SELECT * FROM Users WHERE Username = ?', (user.username,)).fetchone()
    conn.close()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Hashea la contraseña del usuario
    hashed_password = hash_password(user.password)

    # Guarda el usuario en la base de datos
    conn = get_conexion()
    conn.execute(
        'INSERT INTO Users (Username, Password,Role,Email) VALUES (?, ?,?,?)',
        (user.username, hashed_password, user.role, user.email),
    )
    conn.commit()
    conn.close()

    return {"message": "User created successfully"}

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verifica las credenciales del usuario
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crea el token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user['Username'],"Role":user['Role']},expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer","Role":user['Role']}


# Función para verificar token y rol
# Verificación básica del token
async def verify_token(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("Role")
        
        if username is None or role is None:
            raise credentials_exception

        # Retorna el payload decodificado
        return {"username": username, "role": role}
    except JWTError:
        raise credentials_exception

# Función de verificación de rol reutilizable
# Modificar verify_role para aceptar múltiples roles permitidos
def verify_role(allowed_roles: List[str]):
    async def role_dependency(token_data: dict = Depends(verify_token)):
        user_role = token_data.get("role")
        
        # Verificar si el rol del usuario está en la lista de roles permitidos
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Allowed roles: {', '.join(allowed_roles)}",
            )
        
        return token_data

    return role_dependency

@router.get('/getUsers')
async def get_users(token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cur = conn.cursor()
    cur.execute("SELECT Username,Email,Role FROM Users")
    users = cur.fetchall()
    conn.close()
    users_list = [{"Username": user[0], "Email": user[1], "Role": user[2]} for user in users]
    return users_list


   
