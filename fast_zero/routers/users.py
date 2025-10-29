from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import (
    Message,
    Token,
    UserList,
    UserPublic,
    UserSchema,
)
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=UserList)
def read_users(
    session: Session = Depends(get_session), skip: int = 0, limit: int = 100
):
    """Returns a UserList"""
    users = session.scalars(select(User).offset(skip).limit(limit)).all()

    return {'users': users}


@router.get('/{user_id}', response_model=UserPublic)
def get_user(user_id: int, session: Session = Depends(get_session)):
    """Returns a UserSchema user by id"""
    db_user = session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    return db_user


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    """Creates a user in database"""
    db_user = session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already exists',
            )
        if db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT, detail='Email already exists'
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username,
        password=hashed_password,
        email=user.email,
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Updates a user in database by id"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email
        session.commit()
        session.refresh(current_user)

        return current_user

    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        ) from e


@router.delete('/{user_id}', response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Removes a user from database"""

    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


@router.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Endpoint for token based auth"""
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, detail='Incorrect email or password'
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
