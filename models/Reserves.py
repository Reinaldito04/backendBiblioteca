from pydantic import BaseModel
from typing import Optional
class Reserve(BaseModel):
    IDBook : int
    Estado : str 
   
class ReserveUpdate(BaseModel):
    Estado : str