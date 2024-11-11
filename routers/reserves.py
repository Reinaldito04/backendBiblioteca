from fastapi import APIRouter,Depends,HTTPException
from fastapi.responses import JSONResponse
from db.db import get_conexion
from models.Reserves import Reserve
from routers.authUser import verify_role
router = APIRouter(
    prefix="/reserves",
    tags=["reserves"],
    responses={404: {"description": "Not found"}},
)

@router.post("/agg")
async def aggReserve(
    reserve: Reserve,
    token_data: dict = Depends(verify_role(["Admin", "User"]))  # Verifica que el rol sea "Admin" o "User"
):
    conn = get_conexion()
    cursor = conn.cursor()
    
    # Imprimir el contenido de token_data para ver lo que contiene
    
    # Extraer el nombre de usuario del token decodificado
    username = token_data.get("username")  # Aquí extraemos el 'username' desde el token

    # Verificar si no se encuentra el usuario en el token
    if username is None:
        raise HTTPException(status_code=400, detail="Username no encontrado en el token")

    cursor.execute('SELECT ID FROM Users WHERE Username = ?', (username,))
    user_id = cursor.fetchone()

    # Verificar si el usuario existe
    if user_id is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    user_id = user_id[0]  # Obtener el ID del usuario

    # Insertar la reserva en la base de datos
    cursor.execute("INSERT INTO Reserves (IDBook, Estado, IDUser) VALUES (?, ?, ?)",
                   (reserve.IDBook, reserve.Estado, user_id))
    conn.commit()
    conn.close()
    
    # Responder con un mensaje de éxito que incluye el nombre del usuario
    return JSONResponse(content={"message": f"Reserva agregada exitosamente por {username}"}, status_code=200)

@router.get('/get')
async def get_reserves(token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("""
                   
                   SELECT Reserves.ID,Reserves.Estado,Books.Titulo,Books.Autor,Users.Username,Users.Email from Reserves 
                    INNER JOIN Books ON Reserves.IDBook = Books.ID 
                    INNER JOIN Users ON Reserves.IDUser = Users.ID
                   """)
    reserves = cursor.fetchall()
    listReservers = []
    for row in reserves:
        listReservers.append({
            "ID": row[0],
            "Estado": row[1],
            "Titulo": row[2],
            "Autor": row[3],
            "Username": row[4],
            "Email": row[5]
        })
    conn.close()
    return JSONResponse(content={"reserves": listReservers}, status_code=200)