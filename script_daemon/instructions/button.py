import datetime
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import update, table, text
import asyncio


async def turn_on_button(device_id: int,
                         session_maker: async_sessionmaker[AsyncSession]):
    async with session_maker() as session:
        query = text(f'UPDATE buttons SET status = 1 WHERE buttons.id = {device_id}')
        await session.execute(query)
        await session.commit()


async def turn_off_button(device_id: int,
                          session_maker: async_sessionmaker[AsyncSession]):
    async with session_maker() as session:
        query = text(f'UPDATE buttons SET status = 0 WHERE buttons.id = {device_id}')
        await session.execute(query)
        await session.commit()


actions = {1: turn_on_button,
           2: turn_off_button}


def execute_button_action(action_id: int,
                          device_id: int,
                          session_maker: async_sessionmaker[AsyncSession]):
    try:
        print(f'started {action_id}')
        executed_func = actions[action_id]
        asyncio.run(executed_func(device_id=device_id,
                                  session_maker=session_maker))
        print(f'executed {action_id}')
    except:
        pass
