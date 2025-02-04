from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from models.RegisterData import RegisterData, RegisterDataResponse
from db.db import get_conexion
from routers.authUser import verify_role, verify_token
from datetime import datetime

router = APIRouter(
    prefix="/registerData",
    tags=["registerData"],
    responses={404: {"description": "Not found"}},
)


@router.get('/get')
async def get_registerData(token_data: dict = Depends(verify_role(["Admin"]))):
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("""
                   
                   SELECT Registros.userId , Registros.text,Registros.id,Registros.time,Users.Username
                    FROM Registros
                    INNER JOIN Users ON Registros.userId = Users.ID;

                   """)
    
    registerData = cursor.fetchall()
    result = []
    for row in registerData:
        result.append({
            "userId": row[0],
            "text": row[1],
            "id": row[2],
            "time": row[3],
            "Username": row[4]
        })
    conn.close()
    return result


@router.post('/add')
async def add_registerData(registerData: RegisterData, token_data: dict = Depends(verify_role(["Admin"]))):
    # token_data ya contiene los datos decodificados del token
    conn = get_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT ID FROM Users WHERE Username = ?",
                   (token_data.get("username"),))
    user_id = cursor.fetchone() or None
    if user_id is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user_id = user_id[0]
    cursor.execute("INSERT INTO Registros (text,userId,time) VALUES (?,?,?)",
                   (registerData.text, user_id, registerData.time))
    conn.commit()
    conn.close()

    return JSONResponse(content={"message": "RegisterData added successfully"}, status_code=200)

    # cursor.execute("INSERT INTO RegisterData (text,userId,time) VALUES (?,?,?)",
    #                (registerData.text,registerData.userId,registerData.time))
    # conn.commit()
    # conn.close()
    # return JSONResponse(content={"message": "RegisterData added successfully"}, status_code=200)
