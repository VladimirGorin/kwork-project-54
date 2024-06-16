from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from handlers import routers
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from utils import create_jobs_automessage, commons, sender
from middlewares import OuterMiddleware


async def main():
    scheduler = AsyncIOScheduler()
    default = DefaultBotProperties(parse_mode='HTML',
                                   link_preview_is_disabled=True)
    bot = Bot(token=Config.token,
              default=default)
    data = await bot.get_me()
    commons['bot_url'] = f'https://t.me/{data.username}'
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage,
                    scheduler=scheduler)
    for router in routers:
        router.message.outer_middleware(OuterMiddleware())
        router.callback_query.outer_middleware(OuterMiddleware())
    dp.include_routers(*routers)
    scheduler.start()
    #scheduler.add_job(func=run_automessage,
    #                  trigger='interval',
    #                 seconds=Config.interval_automessage,
    #                  args=(Config.interval_automessage, scheduler, bot))
    scheduler.add_job(id='run_jobs',
                      func=sender,
                      trigger='interval',
                      seconds=Config.interval_sending,
                      args=(scheduler, bot))
    scheduler.add_job(id='create_jobs_automessage',
                      func=create_jobs_automessage,
                      trigger='interval',
                      seconds=Config.interval_sending,
                      args=(Config.interval_sending,))
    await dp.start_polling(bot)

if __name__ == '__main__':
    from asyncio import run
    run(main())
