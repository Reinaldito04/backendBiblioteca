from fastapi import APIRouter,Depends
from db.db import get_conexion
from routers.authUser import verify_role
router = APIRouter(
    prefix="/information",
    tags=["information"],
    responses={404: {"description": "Not found"}},
)
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