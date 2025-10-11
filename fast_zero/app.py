from http import HTTPStatus

from fastapi import FastAPI

from fast_zero.schemas import Disgrasa, Message

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Olá mundo!'}


@app.get('/disgrasa', status_code=HTTPStatus.OK, response_model=Disgrasa)
def call_disgrasa():
    return {'disgrasa': 'pudinzao disgrasadao'}
