from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from models.Leans import Lean,LeanResponse
from db.db import get_conexion
from routers.authUser import verify_role
router = APIRouter(
    prefix="/leans",
    tags=["leans"],
    responses={404: {"description": "Not found"}},
)

@router.get('/')
async def get_lean(token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("""
                   
                   SELECT Books.Titulo ,Books.ID,Books.Autor,Leans.IDUser
                   ,Leans.DateStart,Leans.DateEnd,Leans.ID,Users.Username
                    FROM Books
                    INNER JOIN 
                    Leans
                    On Books.ID = Leans.IdBook
                    INNER JOIN 
                    Users 
                    ON Leans.IDUser = Users.ID;

                   """)
    leans =[
        LeanResponse(
            IDBook=row[1],
            Titulo=row[0],
            Autor=row[2],
            LeanID=row[6],
            Username=row[7],
            DateStart=row[4],
            DateEnd=row[5]
        )
        for row in cursor.fetchall()
    ]    
    
    conn.close()
    return leans
   

@router.post('/agg')
async def get_lean_agg(
    
    lean: Lean,
    token_data: dict = Depends(verify_role(["Admin"]))
   ):
    conn = get_conexion()
    cursor = conn.cursor()
    
    # Obtener el ID del usuario
    cursor.execute("SELECT ID FROM Users WHERE Username = ?", (lean.Username,))
    user_id = cursor.fetchone()[0]

    # Verificar si el libro tiene cantidad disponible
    cursor.execute("SELECT cantidad_disponible FROM Books WHERE ID = ?", (lean.IDBook,))
    cantidad_disponible = cursor.fetchone()

    if cantidad_disponible is None or not cantidad_disponible[0].isdigit():
        conn.close()
        return JSONResponse(
            content={"error": "El libro no existe o la cantidad es inválida"},
            status_code=400  # Código de estado para error de solicitud
        )

    # Convertir la cantidad de string a entero
    cantidadDisponible = int(cantidad_disponible[0])

    if cantidadDisponible <= 0:
        conn.close()
        return JSONResponse(
            content={"error": "No hay suficientes copias disponibles del libro"},
            status_code=400  # Código de estado para error de solicitud
        )

    # Insertar el préstamo en la tabla Leans
    cursor.execute(
        "INSERT INTO Leans (IdBook, IDUser, DateStart, DateEnd, DateReal) VALUES (?, ?, ?, ?, ?)",
        (lean.IDBook, user_id, lean.DateStart, lean.DateEnd, "null")
    )

    # Disminuir la cantidad de libros disponibles
    cursor.execute(
        "UPDATE Books SET cantidad_disponible = CAST(cantidad_disponible AS INTEGER) - 1 WHERE ID = ?",
        (lean.IDBook,)
    )

    # Confirmar cambios y cerrar la conexión
    conn.commit()
    conn.close()

    return JSONResponse(
        content={"message": "Préstamo registrado con éxito"},
        status_code=200  # Código de estado para éxito
    )