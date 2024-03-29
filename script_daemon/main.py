import os
from dotenv import load_dotenv
import datetime
import asyncio
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from instructions import execute_button_action

load_dotenv()

DATABASE_URL = os.environ.get('DB_URL')

engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def execute_action(action_id: int,
                         device_id: int,
                         device_type: int,
                         session_maker: async_sessionmaker[AsyncSession]):
    print(f'prepare to run {action_id} on {device_id}')
    match device_type:
        case 1:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, execute_button_action, action_id, device_id, session_maker)


async def get_current_tasks(session_maker: async_sessionmaker[AsyncSession]) -> list:
    async with session_maker() as session:
        query = text("""SELECT script_actions.id, script_actions.action_id, script_actions.device_id, actions.device_type FROM script_actions
         INNER JOIN actions ON actions.id = script_actions.action_id
         WHERE script_actions.id IN
            (SELECT DISTINCT actions_association_table.script_action_id FROM actions_association_table
             INNER JOIN scripts ON scripts.id = actions_association_table.script_id
             WHERE  SEC_TO_TIME((TIME_TO_SEC(CURTIME()) DIV 5) * 5) = ADDTIME(TIMEDIFF(script_actions.latency,'1970-01-01 00:00:00'), scripts.time))""")

        # query = select(Script).options(selectinload(Script.actions))
        result = await session.execute(query)
        result = result.all()
        return result


async def delete_single_scripts(session_maker: async_sessionmaker[AsyncSession]):
    async with session_maker() as session:
        query = text("""SELECT scripts.id FROM scripts
                     WHERE scripts.time
                     BETWEEN SEC_TO_TIME((TIME_TO_SEC(
                         TIME(SUBDATE(CURRENT_TIMESTAMP(), INTERVAL 2 HOUR ))) DIV 5) * 5)
                     AND SEC_TO_TIME((TIME_TO_SEC(
                         TIME(SUBDATE(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR ))) DIV 5) * 5)
                     AND scripts.single_execution = true""")
        result = await session.execute(query)
        script_ids = [script_id[0] for script_id in result]
        if len(script_ids) == 0:
            return
        query = text(f"""DELETE FROM actions_association_table 
            WHERE actions_association_table.script_id 
            IN ({script_ids.__repr__()[1:-1]})""")
        await session.execute(query)
        query = text(f"""DELETE FROM scripts 
            WHERE scripts.id IN ({script_ids.__repr__()[1:-1]})
            AND scripts.single_execution = true""")
        await session.execute(query)
        await session.commit()
        print(script_ids)


async def main():
    result = await get_current_tasks(async_session_maker)
    print(result)
    await asyncio.gather(*[execute_action(script_action[1], script_action[2], script_action[3],
                                          async_session_maker) for script_action in result])
    await delete_single_scripts(async_session_maker)
    end = datetime.datetime.now().time()
    print(end)


if __name__ == "__main__":

    cur_sec = datetime.datetime.now().time().second // 5
    while True:
        if datetime.datetime.now().time().second // 5 != cur_sec:
            cur_sec = datetime.datetime.now().time().second // 5
            asyncio.run(main())
