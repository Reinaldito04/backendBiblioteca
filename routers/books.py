from fastapi import APIRouter,Depends,HTTPException
from models.book import Book,BookResponse,BookUpdate
from db.db import get_conexion
from routers.authUser import verify_role
from typing import List
router = APIRouter(
    prefix="/books",
    tags=["books"],
    responses={404: {"description": "Not found"}},
)

@router.get("/books", response_model=List[BookResponse])
async def read_books(
    token_data: dict = Depends(verify_role(["Admin", "User"]))  # Permitir Admin y User
    
    ):
    conn = get_conexion()
    cursor = conn.execute("SELECT * FROM books")
    books = [
        BookResponse(
            ID=row[0],
            Titulo=row[1],
            Autor=row[2],
            Editorial=row[3],
            anio_publicacion=row[4],
            genero=row[5],
            cantidad_total=row[6],
            cantidad_disponible=row[7],
            Descripcion=row[8],
            Paginas=row[9],
            Ubicacion=row[10],
        )
        for row in cursor.fetchall()
    ]
    conn.close()
    return books

@router.get("/id/{id}")
async def read_book(id: int):
    conn = get_conexion()
    cursor = conn.execute("SELECT * FROM Books WHERE id = ?", (id,))
    book = BookResponse(
        ID=cursor.fetchone()[0],
        Titulo=cursor.fetchone()[1],
        Autor=cursor.fetchone()[2],
        Editorial=cursor.fetchone()[3],
        anio_publicacion=cursor.fetchone()[4],
        genero=cursor.fetchone()[5],
        cantidad_total=cursor.fetchone()[6],
        cantidad_disponible=cursor.fetchone()[7],
        Descripcion=cursor.fetchone()[8],
        Paginas=cursor.fetchone()[9],
        Ubicacion=cursor.fetchone()[10],
    )
    conn.close()
    return book


@router.put("/edit/{id}")
async def edit_book(
    id: int,
    book: BookUpdate,
    token_data: dict = Depends(verify_role(["Admin"]))
):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Books SET Titulo = ?, Autor = ?, genero = ?, cantidad_total = ? WHERE ID = ?",
        (book.Titulo, book.Autor, book.genero, book.cantidad_total, id),
    )
    conn.commit()
    conn.close()
    return {"message": "Book updated successfully"}

@router.delete('/delete/{id}')
async def delete_book(id: int, token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Books WHERE ID = ?", (id,))
    conn.commit()
    conn.close()
    return {"message": "Book deleted successfully"}

@router.post("/agg")
async def create_book(
    book: Book, 
    token_data: dict = Depends(verify_role(["Admin"]))
):
    conn = get_conexion()
    # Comprobar si ya existe un libro con el mismo título y autor
    cursor = conn.execute(
        "SELECT * FROM Books WHERE Titulo = ? AND Autor = ?",
        (book.Titulo, book.Autor)
    )
    existing_book = cursor.fetchone()
    
    if existing_book:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Ya hay un libro con el mismo autor y titulo registrado, intenta con otro o aumenta su stock en el sistema."
        )

    # Si no existe, se realiza la inserción
    cursor = conn.execute(
        "INSERT INTO Books (Titulo, Autor, Editorial, anio_publicacion, genero, cantidad_total, cantidad_disponible, Descripcion, Paginas, Ubicacion) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            book.Titulo,
            book.Autor,
            book.Editorial,
            book.anio_publicacion,
            book.genero,
            book.cantidad_total,
            book.cantidad_disponible,
            book.Descripcion,
            book.Paginas,
            book.Ubicacion
        ),
    )
    conn.commit()
    conn.close()
    return {"message": "Book created"}


