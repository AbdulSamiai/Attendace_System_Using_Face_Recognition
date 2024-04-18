from pydantic import BaseModel
class Person(BaseModel):
    name:str
    time:str
    day:str