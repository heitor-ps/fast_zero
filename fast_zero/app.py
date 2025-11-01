from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.routers import auth, users
from fast_zero.schemas import Disgrasa, Message

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    """Defines a dummy function"""
    return {'message': 'Olá mundo!'}


@app.get('/disgrasa', status_code=HTTPStatus.OK, response_model=Disgrasa)
def call_disgrasa():
    """Returns a disgrasa dictionary"""
    return {'disgrasa': 'pudinzao disgrasadao'}
