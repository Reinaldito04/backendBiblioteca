from pydantic import BaseModel

class Fines(BaseModel):
    IDLean : int 
    Username : str
    IDLibro : int
    Estado : str 
    MontoMulta : str