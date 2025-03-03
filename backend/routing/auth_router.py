from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Body
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from schemas.users import UserRegister
from schemas.books import Book
from depends import get_book_service, get_user_service
from schemas.users import UserRegister, UserLogin, User
from services.books import BookService
from services.users import UserService
from utils.security import get_password_hash


router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")



@router.post("/register")
async def register_user(user_data: UserRegister,
                        user_service: UserService = Depends(get_user_service)) -> dict:

    if await user_service.register(user_data):
        return {'message': 'Вы успешно зарегистрированы!'}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует!"
        )



from fastapi import Form

@router.post("/login")
async def login_user(
    username: Optional[str] = Form(default=None),
    password: Optional[str] = Form(default=None),
    user_data: Optional[UserLogin] = Body(default=None),
    user_service: UserService = Depends(get_user_service)
) -> dict:
    if user_data:
        final_user_data = user_data
    elif username and password:
        final_user_data = UserLogin(username=username, password=password)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректные данные",
        )
    access_token = await user_service.login(final_user_data)
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me/")
async def get_me(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    current_user = await user_service.get_current_user(token)
    return current_user



