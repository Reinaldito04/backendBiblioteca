from pydantic import BaseModel
from typing import Optional

class Lean(BaseModel):
    IDBook : int
    Username : str 
    DateStart : str 
    DateEnd : str
    
class LeanResponse(BaseModel):
    IDBook : int
    Titulo : str
    Autor: str 
    LeanID : int
    Username : str 
    DateStart : str 
    DateEnd : str
    DateReal: Optional[str]  # Permite None como valor válido
    
class LeanUpdate(BaseModel):
    DateReal : str
    
    