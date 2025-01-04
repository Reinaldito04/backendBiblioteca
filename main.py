from fastapi import FastAPI
from routers.books import router as book
from routers.authUser import router as auth 
from fastapi.middleware.cors import CORSMiddleware
from routers.leans import router as leans
from routers.fines import router as fines 
from routers.reserves import router as reservers
from routers.information import router as information
from routers.registerData import router as registerData


app = FastAPI()
app.include_router(book)
app.include_router(auth)
app.include_router(leans)
app.include_router(fines)
app.include_router(reservers)
app.include_router(information)
app.include_router(registerData)

origins = [
    "http://localhost:3000",  # Tu frontend en desarrollo (ajusta según sea necesario)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permitir los orígenes definidos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
