import os
from dotenv import load_dotenv
import datetime
import asyncio
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from instructions import execute_button_action
import argparse

load_dotenv()

DATABASE_URL = os.environ.get('DB_URL')

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def execute_action(action_id: int,
                         device_id: int,
                         session_maker: async_sessionmaker[AsyncSession]):
    print(f'prepare to run {action_id} on {device_id}')
    match device_id:
        case 1:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, execute_button_action, action_id, device_id, session_maker)


async def get_current_tasks(session_maker: async_sessionmaker[AsyncSession]) -> list:
    async with session_maker() as session:
        query = text("""SELECT * FROM script_actions WHERE 
            (SELECT script_id FROM actions_association_table WHERE 
             actions_association_table.script_action_id = script_actions.id)
            IN 
            (SELECT scripts.id FROM scripts 
            WHERE SEC_TO_TIME((TIME_TO_SEC(CURTIME()) DIV 60) * 60) = ADDTIME(TIMEDIFF(script_actions.latency,'1970-01-01 00:00:00'), scripts.time))""")

        # query = select(Script).options(selectinload(Script.actions))
        result = await session.execute(query)
        result = result.all()
        return result


async def main(sleep_time: int = 1):
    result = await get_current_tasks(async_session_maker)
    print(result)
    await asyncio.gather(*[execute_action(script_action[1], script_action[2],
                                          async_session_maker) for script_action in result])
    end = datetime.datetime.now().time()
    print(end)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", '--sleeptime', type=float)
    args = parser.parse_args()
    cur_min = datetime.datetime.now().time().minute
    print(args.sleeptime)
    if args.sleeptime is not None:
        while True:
            if datetime.datetime.now().time().minute != cur_min:
                cur_min = datetime.datetime.now().time().minute
                asyncio.run(main(args.sleeptime))
    else:
        while True:
            if datetime.datetime.now().time().minute != cur_min:
                cur_min = datetime.datetime.now().time().minute
                asyncio.run(main())