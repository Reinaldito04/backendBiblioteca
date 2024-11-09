from pydantic import BaseModel

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
    DateReal : str
    
class LeanUpdate(BaseModel):
    DateReal : str
    
    