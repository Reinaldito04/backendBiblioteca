from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from models.Leans import Lean, LeanResponse, LeanUpdate
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
                   ,Leans.DateStart,Leans.DateEnd,Leans.ID,Users.Username,Leans.DateReal
                    FROM Books
                    INNER JOIN 
                    Leans
                    On Books.ID = Leans.IdBook
                    INNER JOIN 
                    Users 
                    ON Leans.IDUser = Users.ID;

                   """)
    leans = [
        LeanResponse(
            IDBook=row[1],
            Titulo=row[0],
            Autor=row[2],
            LeanID=row[6],
            Username=row[7],
            DateStart=row[4],
            DateEnd=row[5],
            DateReal='No entregado aún' if row[8] is None else row[8],  # Maneja valores nulos aquí

        )
        for row in cursor.fetchall()
    ]

    conn.close()
    return leans

# Endpoint para actualizar la fecha de entrega de un préstamo

@router.get('/username/{name}/{title}')
async def get_lean(name : str , title : str,token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT Books.Titulo ,Books.ID,Books.Autor,Leans.IDUser
                   ,Leans.DateStart,Leans.DateEnd,Leans.ID,Users.Username,Leans.DateReal
                    FROM Books
                    INNER JOIN 
                    Leans
                    On Books.ID = Leans.IdBook
                    INNER JOIN 
                    Users 
                    ON Leans.IDUser = Users.ID
                    WHERE Users.Username = ? AND Books.Titulo = ?;
                   """, (name,title))
    leans = [
        LeanResponse(
            IDBook=row[1],
            Titulo=row[0],
            Autor=row[2],
            LeanID=row[6],
            Username=row[7],
            DateStart=row[4],
            DateEnd=row[5],
            DateReal='No entregado aún' if row[8] is None else row[8],  # Maneja valores nulos aquí
        )
        for row in cursor.fetchall()
    ]

    conn.close()
    return leans

@router.get('/username/{name}')
async def get_lean(name : str,token_data: dict = Depends(verify_role(["Admin","User"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT Books.Titulo ,Books.ID,Books.Autor,Leans.IDUser
                   ,Leans.DateStart,Leans.DateEnd,Leans.ID,Users.Username,Leans.DateReal
                    FROM Books
                    INNER JOIN 
                    Leans
                    On Books.ID = Leans.IdBook
                    INNER JOIN 
                    Users 
                    ON Leans.IDUser = Users.ID
                    WHERE Users.Username = ?;
                   """, (name,))
    leans = [
    LeanResponse(
        IDBook=row[1],
        Titulo=row[0],
        Autor=row[2],
        LeanID=row[6],
        Username=row[7],
        DateStart=row[4],
        DateEnd=row[5],
        DateReal='No entregado aún' if row[8] is None else row[8],  # Manejo de None
    )
    for row in cursor.fetchall()
]


    conn.close()
    return leans


@router.put('/update/{id}')
async def update_lean(id: int, lean: LeanUpdate, token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("UPDATE Leans SET DateReal = ? WHERE ID = ?",
                   (lean.DateReal, id))

    cursor.execute("""
                   SELECT IdBook FROM Leans WHERE ID = ?;
                   
                   """, (id,))
    IdBook = cursor.fetchone()[0]

    # Disminuir la cantidad de libros disponibles
    cursor.execute(
        "UPDATE Books SET cantidad_disponible = CAST(cantidad_disponible AS INTEGER) + 1 WHERE ID = ?",
        (IdBook,)
    )

    conn.commit()

    conn.close()
    return {"message": "Prestamo entregado correctamente"}


@router.post('/agg')
async def get_lean_agg(
    lean: Lean,
    token_data: dict = Depends(verify_role(["Admin"]))
):
    conn = get_conexion()
    cursor = conn.cursor()

    # Obtener el ID del usuario
    cursor.execute("SELECT ID FROM Users WHERE Username = ?", (lean.Username,))
    user_data = cursor.fetchone()

    if not user_data:
        conn.close()
        return JSONResponse(
            content={"error": "El usuario no existe"},
            status_code=400
        )

    user_id = user_data[0]


 # Verificar si el usuario tiene multas pendientes
    cursor.execute(
        "SELECT COUNT(*) FROM Fines WHERE UserID = ? AND Estado = 'No pagada'",
        (user_id,)
    )
    multas_pendientes = cursor.fetchone()[0]

    if multas_pendientes > 0:
        conn.close()
        return JSONResponse(
            content={"error": "El usuario tiene multas pendientes y no puede realizar préstamos"},
            status_code=400
        )

    # Verificar si el usuario ya tiene 3 préstamos activos
    cursor.execute(
        "SELECT COUNT(*) FROM Leans WHERE IDUser = ? AND DateReal IS NULL",
        (user_id,)
    )
    prestamos_activos = cursor.fetchone()[0]

    if prestamos_activos >= 3:
        conn.close()
        return JSONResponse(
            content={"error": "El usuario ya tiene 3 préstamos activos"},
            status_code=400
        )

    # Verificar si el libro tiene cantidad disponible
    cursor.execute(
        "SELECT cantidad_disponible FROM Books WHERE ID = ?", (lean.IDBook,)
    )
    cantidad_disponible = cursor.fetchone()

    if cantidad_disponible is None or not cantidad_disponible[0].isdigit():
        conn.close()
        return JSONResponse(
            content={"error": "El libro no existe o la cantidad es inválida"},
            status_code=400
        )

    # Convertir la cantidad de string a entero
    cantidadDisponible = int(cantidad_disponible[0])

    if cantidadDisponible <= 0:
        conn.close()
        return JSONResponse(
            content={"error": "No hay suficientes copias disponibles del libro"},
            status_code=400
        )

    # Insertar el préstamo en la tabla Leans
    cursor.execute(
        "INSERT INTO Leans (IdBook, IDUser, DateStart, DateEnd, DateReal) VALUES (?, ?, ?, ?, ?)",
        (lean.IDBook, user_id, lean.DateStart, lean.DateEnd, None)
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
        status_code=200
    )
