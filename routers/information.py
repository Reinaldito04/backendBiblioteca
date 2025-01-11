from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import JSONResponse,FileResponse,StreamingResponse
from db.db import get_conexion
from routers.authUser import verify_role
import os
import aiofiles
import shutil
from typing import Generator
from fastapi.staticfiles import StaticFiles

router = APIRouter(
    prefix="/information",
    tags=["information"],
    responses={404: {"description": "Not found"}},
)
router.mount("/db", StaticFiles(directory="db"), name="db")

DATABASE_PATH = "db/db.db"  # Cambia esta ruta a la ubicación de tu archivo SQLite
BACKUP_PATH = "db/backup.db"  # Cambia esta ruta a la ubicación de la copia de seguridad
def create_backup():
    # Lógica para hacer el respaldo de la base de datos
    backup_filename = "backup.db"
    backup_path = os.path.join("db", backup_filename)
    
    # Aquí puedes generar el respaldo de la base de datos en el archivo `backup.db`
    # Simulación de respaldo: simplemente copiamos un archivo de ejemplo
    shutil.copy("db/db.db", backup_path)  # Esto es solo un ejemplo

    return backup_path

@router.get("/backup")
async def download_backup():
    # Crea el respaldo
    backup_path = create_backup()

    # Devuelve el archivo de respaldo
    return FileResponse(backup_path, media_type='application/octet-stream', filename='backup.db')

@router.get("/getBooksCantity")
async def get_books_cantity( token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Books")
    cantity = cursor.fetchone()[0]
    conn.close()
    return {"cantity": cantity}

@router.get("/getBooksStock")
async def get_books_stock(token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    # Consulta para sumar la cantidad total de libros disponibles
    cursor.execute("SELECT SUM(cantidad_total) FROM Books")
    stock = cursor.fetchone()[0] or 0  # Maneja el caso en que el resultado sea `None`
    conn.close()
    return {"cantity": stock}

@router.get('/getFinesCantity')
async def get_fines_cantity(token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Fines")
    cantity = cursor.fetchone()[0]
    conn.close()
    return {"cantity": cantity}

@router.get('/getLeans')
async def get_leans(token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Leans")
    cantity = cursor.fetchone()[0]
    conn.close()
    return {"cantity": cantity}

@router.get('/getReservesCantity')
async def get_reserves_cantity(token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Reserves WHERE Estado = 'Reservado'")
    cantity = cursor.fetchone()[0]
    conn.close()
    return {"cantity": cantity}

@router.get('/getCantityUsers')
async def get_cantity_users(token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Users WHERE Role = 'User'" )
    cantity = cursor.fetchone()[0]
    conn.close()
    return {"cantity": cantity}

@router.get('/getUserInfo')
async def get_user_info(token_data: dict = Depends(verify_role(["Admin","User"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute('SELECT Username,Email,Role FROM Users WHERE Username = ?', (token_data['username'],))
    result = cursor.fetchone()
    
    conn.close()
    return {
        "username": result[0],
        "email": result[1],
        "role": result[2]
    }