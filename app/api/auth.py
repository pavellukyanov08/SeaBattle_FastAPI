from datetime import timedelta

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from starlette.status import HTTP_409_CONFLICT, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.models import Player
from app.schemas.auth import Token
from app.schemas.player import PlayerRegister, PlayerResponse
from app.core.auth import get_user, get_hashed_password, authenticate_user, create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/players/register", response_model=PlayerResponse)
async def register(user_data: PlayerRegister, db: AsyncSession = Depends(get_session)):
    """
    Регистрирует пользователя в системе
    :param user_data: пользовательские данные (имя пользователя и пароль)
    :param db:
    :return:
    """
    existing_user = await get_user(db, user_data.username)
    if existing_user:
       raise HTTPException(status_code=HTTP_409_CONFLICT, detail="Такой пользователь уже зарегистрирован")

    if len(user_data.password) < 5:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Слишком короткий пароль")

    hashed_password = get_hashed_password(user_data.password)

    new_player =  Player(
        name=user_data.username,
        hashed_password=hashed_password
    )

    db.add(new_player)
    await db.commit()
    await db.refresh(new_player)

    return new_player


@router.post('/players/login', response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    """
    Авторизация пользователя в системе
    :param form_data: форма с пользовательскими данными
    :param db:
    :return:
    """
    existing_user = await authenticate_user(db, form_data.username, form_data.password)
    if not existing_user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(days=1)
    access_token = create_access_token(
        data={'sub': existing_user.name},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


