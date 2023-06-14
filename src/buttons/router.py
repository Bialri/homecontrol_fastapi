from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from secrets import token_urlsafe
from fastapi_jwt_auth import AuthJWT

from src.database import get_async_session
from .models import Button
from .schemas import ButtonSchema, ButtonUpdateSchema, ButtonWithTokenSchema, ButtonResponseSchema
from src.auth.models import User

router = APIRouter(
    prefix="/buttons",
    tags=["Buttons"]
)


@router.get("/")
async def get_all_buttons(session: AsyncSession = Depends(get_async_session),
                          authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    subject = authorize.get_jwt_subject()
    user = await session.execute(select(User).where(User.username == subject))
    user = user.scalar()
    query = select(Button).where(Button.owner == user)
    result = await session.execute(query)
    result = result.scalars()
    result = [ButtonResponseSchema.from_orm(btn).dict() for btn in result]
    return {'status': 'Success get',
            'data': result,
            'detail': ''}


@router.post("/")
async def add_button(new_button: ButtonSchema,
                     session: AsyncSession = Depends(get_async_session),
                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    subject = authorize.get_jwt_subject()
    user = await session.execute(select(User).where(User.username == subject))
    user = user.scalar()
    button = Button(**new_button.dict(), owner_id=user.id)
    token = token_urlsafe(40)[:39]
    button.token = token
    session.add(button)
    await session.commit()
    result = ButtonWithTokenSchema.from_orm(button).dict()
    return {'status': 'Success create',
            'data': result,
            'detail': ''}


@router.patch('/{button_pk}')
async def update_button(button_pk: int,
                        updated_button: ButtonUpdateSchema,
                        response_status: Response,
                        session: AsyncSession = Depends(get_async_session),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    subject = authorize.get_jwt_subject()
    user = await session.execute(select(User).where(User.username == subject))
    user = user.scalar()
    query = update(Button).values(**updated_button.dict(exclude_none=True)).where(Button.id == button_pk,
                                                                                  Button.owner_id == user.id)
    update_query = await session.execute(query)
    if update_query.rowcount == 0:
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        session.rollback()
        return {'status': 'fail update',
                'data': '',
                'detail': 'Button object not found'}
    await session.commit()
    response_query = select(Button).where(Button.id == button_pk, Button.owner_id == user.id)
    response = await session.execute(response_query)
    response = ButtonSchema.from_orm(response.scalar()).dict()
    return {'status': 'Success update',
            'data': response,
            'detail': ''}


@router.delete('/{button_pk}')
async def delete_button(button_pk: int,
                        response_status: Response,
                        session: AsyncSession = Depends(get_async_session),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    subject = authorize.get_jwt_subject()
    user = await session.execute(select(User).where(User.username == subject))
    user = user.scalar()
    query = delete(Button).where(Button.id == button_pk, Button.owner_id == user.id)
    result = await session.execute(query)
    print(result.rowcount)
    if result.rowcount == 0:
        await session.rollback()
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        return {'status': 'fail update',
                'data': '',
                'detail': 'Button object not found'}
    await session.commit()
    return {'status': 'Success delete',
            'data': '',
            'detail': ''}

@router.get('/GetWithToken/')
async def get_with_token(token: str,
                         response_status: Response,
                         session: AsyncSession = Depends(get_async_session)):
    query = select(Button).where(Button.token == token)
    result = await session.execute(query)
    result = result.all()
    if len(result) == 0:
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        return {'status': 'Failed get',
                'data': '',
                'detail': 'Wrong token'}
    response = ButtonSchema.from_orm(result[0][0]).dict()
    return {'status': 'Success Get',
            'data': response,
            'detail': ''}


@router.get('/activedevices')
async def get_active_devices(session: AsyncSession = Depends(get_async_session)):
    active_devices = [{'id': 1, 'name': 'button'},
                      {'id': 2, 'name': 'slider'}, ]
    return {'status': 'Success get',
            'data': active_devices,
            'detail': ''}
