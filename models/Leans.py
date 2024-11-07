from pydantic import BaseModel

class Lean(BaseModel):
    IDBook : int
    Username : str 
    DateStart : str 
    DateEnd : str