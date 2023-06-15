from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select, delete, update, text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import selectinload

from src.database import get_async_session
from .models import Device, Action, ScriptAction, Script, ActionsAssociation
from .schemas import (DevicesResponseSchema, DeviceCreateSchema, ActionResponseSchema,
                      ActionCreateSchema, ScriptActionResponseSchema, ScriptActionCreateSchema,
                      ScriptResponseSchema, ScriptCreateSchema, ScriptActionUpdateSchema,
                      ScriptUpdateSchema)
from src.auth.models import User
from src.config import SCRIPTS_ADD_SECRET

router = APIRouter(
    prefix='/scripts',
    tags=['Scripts']
)


@router.get('/devices')
async def get_devices(session: AsyncSession = Depends(get_async_session),
                      authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    query = select(Device)
    result = await session.execute(query)
    response = [DevicesResponseSchema.from_orm(device[0]) for device in result.all()]
    return {'status': 'Success get',
            'data': response,
            'detail': ''}


@router.post('/devices')
async def create_device(new_device: DeviceCreateSchema,
                        response_status: Response,
                        session: AsyncSession = Depends(get_async_session),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    if SCRIPTS_ADD_SECRET != new_device.secret:
        response_status.status_code = status.HTTP_403_FORBIDDEN
        return {'status': 'Failed create',
                'data': '',
                'detail': 'Wrong Secret'}
    device_args = new_device.dict()
    device_args.pop('secret')
    device = Device(**device_args)
    session.add(device)
    await session.commit()
    response = DevicesResponseSchema.from_orm(device).dict()
    return {'status': 'Success create',
            'data': response,
            'detail': ''}


@router.get('/actions/{device_id}')
async def get_device_actions(device_id: int,
                             response_status: Response,
                             session: AsyncSession = Depends(get_async_session),
                             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    query = select(Action).where(Action.device_type == device_id)
    result = await session.execute(query)
    result = result.all()
    if len(result) == 0:
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        return {'status': 'Failed get',
                'data': '',
                'detail': 'Wrong device id'}
    response = [ActionResponseSchema.from_orm(action[0]) for action in result]
    return {'status': 'Success get',
            'data': response,
            'detail': ''}


@router.post('/actions')
async def create_device(new_action: ActionCreateSchema,
                        response_status: Response,
                        session: AsyncSession = Depends(get_async_session),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    if SCRIPTS_ADD_SECRET != new_action.secret:
        response_status.status_code = status.HTTP_403_FORBIDDEN
        return {'status': 'Failed create',
                'data': '',
                'detail': 'Wrong Secret'}
    action_args = new_action.dict()
    action_args.pop('secret')
    action = Action(**action_args)
    session.add(action)
    await session.commit()
    response = ActionResponseSchema.from_orm(action).dict()
    return {'status': 'Success create',
            'data': response,
            'detail': ''}


@router.get('/script_actions/{script_id}')
async def get_script_actions(script_id: int,
                             response_status: Response,
                             session: AsyncSession = Depends(get_async_session),
                             authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    query = select(Script).options(selectinload(Script.actions)).where(Script.id == script_id)
    result = await session.execute(query)
    result = result.all()
    if len(result) == 0:
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        return {'status': 'Failed get',
                'data': '',
                'detail': 'Wrong device id'}
    result = result[0][0]
    script_actions = result.actions
    response = [ScriptActionResponseSchema.from_orm(script_action) for script_action in script_actions]
    return {'status': 'Success get',
            'data': response,
            'detail': ''}


@router.post('/script_actions')
async def create_device(new_script_action: ScriptActionCreateSchema,
                        response_status: Response,
                        session: AsyncSession = Depends(get_async_session),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    subject = authorize.get_jwt_subject()
    user = await session.execute(select(User).where(User.username == subject))
    user = user.scalar()
    script = select(Script).where(Script.id == new_script_action.script_id, Script.owner_id == user.id)
    script = await session.execute(script)
    script = script.all()
    if len(script) == 0:
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        return {'status': 'Failed create',
                'data': '',
                'detail': 'Wrong script_id'}
    script = script[0][0]
    script_action_args = new_script_action.dict()
    script_action_args.pop('script_id')
    script_action = ScriptAction(**script_action_args)
    session.add(script_action)
    await session.commit()
    association = ActionsAssociation(script_action_id=script_action.id, script_id=script.id)
    session.add(association)
    await session.commit()
    response = ScriptActionResponseSchema.from_orm(script_action).dict()
    return {'status': 'Success create',
            'data': response,
            'detail': ''}


@router.patch('/script_actions/{script_action_id}')
async def update_script_action(script_action_id: int,
                               updated_script_action: ScriptActionUpdateSchema,
                               response_status: Response,
                               session: AsyncSession = Depends(get_async_session),
                               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    query = update(ScriptAction).values(**updated_script_action.dict(exclude_none=True)).where(
        ScriptAction.id == script_action_id)
    update_result = await session.execute(query)
    if update_result.rowcount == 0:
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        session.rollback()
        return {'status': 'Fail update',
                'data': '',
                'detail': 'ScriptAction object not found'}
    await session.commit()
    response_query = select(ScriptAction).where(ScriptAction.id == script_action_id)
    response = await session.execute(response_query)
    response = ScriptActionResponseSchema.from_orm(response.scalar()).dict()
    return {'status': 'Success update',
            'data': response,
            'detail': ''}


@router.delete('/script_actions/{script_action_id}')
async def delete_script_action(script_action_id: int,
                               response_status: Response,
                               session: AsyncSession = Depends(get_async_session),
                               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    query = delete(ActionsAssociation).where(ActionsAssociation.script_action_id == script_action_id)
    asociation_result = await session.execute(query)
    query = delete(ScriptAction).where(ScriptAction.id == script_action_id)
    script_action_result = await session.execute(query)
    await session.commit()

    if asociation_result.rowcount == 0 and script_action_result.rowcount == 0:
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        return {'status': 'Failed delete',
                'data': '',
                'detail': 'Wrong script_action_id'}

    return {'status': 'Success delete',
            'data': '',
            'detail': ''}


@router.get('/script')
async def get_script(session: AsyncSession = Depends(get_async_session),
                     authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    subject = authorize.get_jwt_subject()
    user = await session.execute(select(User).where(User.username == subject))
    user = user.scalar()
    query = select(Script).where(Script.owner_id == user.id)
    result = await session.execute(query)
    result = result.all()
    response = [ScriptResponseSchema.from_orm(script[0]) for script in result]
    return {'status': 'Success get',
            'data': response,
            'detail': ''}


@router.post('/script')
async def create_script(new_script: ScriptCreateSchema,
                        session: AsyncSession = Depends(get_async_session),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    subject = authorize.get_jwt_subject()
    user = await session.execute(select(User).where(User.username == subject))
    user = user.scalar()
    script = Script(**new_script.dict(), owner_id=user.id)
    session.add(script)
    await session.commit()
    response = ScriptResponseSchema.from_orm(script).dict()
    return {'status': 'Success create',
            'data': response,
            'detail': ''}


@router.patch('/script/{script_id}')
async def update_script_action(script_id: int,
                               update_script: ScriptUpdateSchema,
                               response_status: Response,
                               session: AsyncSession = Depends(get_async_session),
                               authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    query = update(Script).values(**update_script.dict(exclude_none=True)).where(
        Script.id == script_id)
    update_result = await session.execute(query)
    if update_result.rowcount == 0:
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        session.rollback()
        return {'status': 'Fail update',
                'data': '',
                'detail': 'Script object not found'}
    await session.commit()
    response_query = select(Script).where(Script.id == script_id)
    response = await session.execute(response_query)
    response = ScriptResponseSchema.from_orm(response.scalar()).dict()
    return {'status': 'Success update',
            'data': response,
            'detail': ''}


@router.delete('/script/{script_id}')
async def delete_script(script_id: int,
                        response_status: Response,
                        session: AsyncSession = Depends(get_async_session),
                        authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    query = select(ActionsAssociation.script_action_id).where(ActionsAssociation.script_id == script_id)
    result_select = await session.execute(query)
    result_select = result_select.all()

    query = delete(ActionsAssociation).where(ActionsAssociation.script_id == script_id)
    result_asociation = await session.execute(query)

    query = delete(ScriptAction).where(ScriptAction.id
                                       .in_([script_action_id[0] for script_action_id in result_select]))
    result_script_actions = await session.execute(query)

    query = delete(Script).where(Script.id == script_id)
    result_scripts = await session.execute(query)
    if result_scripts.rowcount == 0:
        response_status.status_code = status.HTTP_400_BAD_REQUEST
        await session.rollback()
        return {'status': 'Failed delete',
                'data': '',
                'detail': 'Wrong script_id'}
    await session.commit()
    return {'status': 'Success delete',
            'data': '',
            'detail': ''}


@router.get('/curtime')
async def get_curtime(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(text('SELECT CURTIME()'))
    print(result.scalar())
    return ""
