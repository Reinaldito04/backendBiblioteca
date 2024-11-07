from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    Titulo: str
    Autor: str
    Editorial : str 
    anio_publicacion: Optional[str]
    genero: str
    cantidad_total : str 
    cantidad_disponible : str
    Descripcion : str 
    Paginas : str
    Ubicacion : Optional[str] 

class BookResponse(Book):
    ID: int
 
class BookUpdate(BaseModel):
    Titulo: str
    Autor: str
    genero: str
    cantidad_total: str
        