from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Disgrasa(BaseModel):
    disgrasa: str
