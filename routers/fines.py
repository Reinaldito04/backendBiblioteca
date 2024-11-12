from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from models.Fines import Fines
from db.db import get_conexion
from routers.authUser import verify_role
from datetime import datetime

router = APIRouter(
    prefix="/fines",
    tags=["fines"],
    responses={404: {"description": "Not found"}},
)

@router.post("/agg")
async def get_lean_agg(

    fines: Fines,
    token_data: dict = Depends(verify_role(["Admin"]))
):
    conn = get_conexion()
    cursor = conn.cursor()

    # Obtener el ID del usuario
    cursor.execute("SELECT ID FROM Users WHERE Username = ?", (fines.Username,))
    user_id = cursor.fetchone()[0]
   
    cursor.execute("INSERT INTO Fines ( UserID,IDLibro,MontoMulta,Estado,IDlean) VALUES (?,?,?,?,?)",
                   (user_id,fines.IDLibro,fines.MontoMulta,fines.Estado,fines.IDLean))
    conn.commit()
    conn.close()
    return JSONResponse(content={"message": "Fine added successfully"}, status_code=200)    


@router.get("/getFines")
async def get_fines(token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT Fines.ID, Fines.Estado, Fines.MontoMulta, Leans.DateStart, Leans.DateEnd, Books.Titulo, Books.Autor, Users.Username 
        FROM Fines 
        INNER JOIN Leans on Fines.IDlean = Leans.ID
        INNER JOIN Books on Fines.IDLibro = Books.ID
        INNER JOIN Users on Fines.UserID = Users.ID
    """)
    
    fines = cursor.fetchall()
    listFines = []
    for row in fines:
        # Convertir DateEnd a un objeto datetime
        date_end = datetime.strptime(row[4], "%Y-%m-%d")  # Asegúrate de que el formato coincide con tu base de datos
        current_date = datetime.now()
        
        # Calcular los días de retraso (si existe)
        delay_days = (current_date - date_end).days if current_date > date_end else 0
        
        listFines.append({
            "ID": row[0],
            "Estado": row[1],
            "MontoMulta": row[2],
            "DateStart": row[3],
            "DateEnd": row[4],
            "Titulo": row[5],
            "Autor": row[6],
            "Username": row[7],
            "DiasRetraso": delay_days  # Añadir los días de retraso
        })
    
    conn.close()
    return listFines
    
@router.get('/getFines/{username}')
async def get_fines_by_username(username: str, token_data: dict = Depends(verify_role(["Admin","User"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Fines.ID, Fines.Estado, Fines.MontoMulta, Leans.DateStart, Leans.DateEnd, Books.Titulo, Books.Autor, Users.Username 
        FROM Fines 
        INNER JOIN Leans on Fines.IDlean = Leans.ID
        INNER JOIN Books on Fines.IDLibro = Books.ID
        INNER JOIN Users on Fines.UserID = Users.ID
        WHERE Users.Username = ?
    """, (username,))
    fines = cursor.fetchall()
    listFines = []
    for row in fines:
        # Convertir DateEnd a un objeto datetime
        date_end = datetime.strptime(row[4], "%Y-%m-%d")  # Asegúrate de que el formato coincide con tu base de datos
        current_date = datetime.now()
        
        # Calcular los días de retraso (si existe)
        delay_days = (current_date - date_end).days if current_date > date_end else 0
        
        listFines.append({
            "ID": row[0],
            "Estado": row[1],
            "MontoMulta": row[2],
            "DateStart": row[3],
            "DateEnd": row[4],
            "Titulo": row[5],
            "Autor": row[6],
            "Username": row[7],
            "DiasRetraso": delay_days  # Añadir los días de retraso
        })
    
    conn.close()
    return listFines
    
