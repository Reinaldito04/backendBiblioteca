from pydantic import BaseModel

class RegisterData(BaseModel):
    text:str
    time : str 
    
class RegisterDataResponse(RegisterData):
    ID : int