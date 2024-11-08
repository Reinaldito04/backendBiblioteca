from fastapi import FastAPI
from routers.books import router as book
from routers.authUser import router as auth 
from fastapi.middleware.cors import CORSMiddleware
from routers.leans import router as leans
app = FastAPI()

app.include_router(book)
app.include_router(auth)
app.include_router(leans)

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
