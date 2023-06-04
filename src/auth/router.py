from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi_jwt_auth import AuthJWT

from .schemas import UserCreateSchema, UserReadSchema, UserAuthSchema
from src.database import get_async_session
from .models import User
from .utils import get_hashed_password, check_password
from .config import Settings



router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)


@AuthJWT.load_config
def get_config():
    return Settings()


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_user(new_user: UserCreateSchema,
                      response_status: Response,
                      session: AsyncSession = Depends(get_async_session)):
    emails = await session.execute(select(User.email))
    emails = emails.all()
    if any(new_user.email in email for email in emails):
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        return {'status': 'Failed create',
                'data': '',
                'detail': 'User with given email already exist'}
    password = new_user.password
    del new_user.password
    hashed_password = get_hashed_password(password)
    user = User(**new_user.dict())
    user.hashed_password = hashed_password
    session.add(user)
    await session.commit()
    result = UserReadSchema.from_orm(user).dict()
    return {'status': 'Success create',
            'data': result,
            'detail': ''}


@router.post('/login')
async def authenticate_user(credentials: UserAuthSchema,
                            response_status: Response,
                            session: AsyncSession = Depends(get_async_session),
                            authorize: AuthJWT = Depends()):
    user_query = select(User).where(User.email == credentials.email)
    user = await session.execute(user_query)
    user = user.scalar()
    if user is None or not check_password(credentials.password, user.hashed_password):
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        return {'status': "Failed authentication",
                'data': '',
                'details': 'Bad credentials'}
    access_token = authorize.create_access_token(subject=user.username)
    refresh_token = authorize.create_refresh_token(subject=user.username)
    result = {'access': access_token,
              'refresh': refresh_token}
    return {'status': 'Success authentication',
            'data': result,
            'detail': ''}


@router.post('/refresh')
async def refresh_user_token(authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()
    user = authorize.get_jwt_subject()
    new_access_token = authorize.create_access_token(subject=user)
    new_refresh_token = authorize.create_refresh_token(subject=user)
    result = {'access': new_access_token,
              'refresh': new_refresh_token}
    return {'status': 'Success refresh',
            'data': result,
            'detail': ''}
