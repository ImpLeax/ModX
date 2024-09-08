import asyncio
import logging
from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from app.handlers import router_admin, router_user, router, router_messages, router_congat, router_profinity
from app.middlewares.middleware import AntiFloodMiddleware
from redis.asyncio import Redis


load_dotenv()
TOKEN = getenv('TOKEN')
ADMIN = int(getenv('ADMIN'))
bot = Bot(TOKEN)


router_admin.message.filter(F.chat.type == "supergroup")
router_admin.message.filter(F.from_user.id == ADMIN)
router_user.message.filter(F.chat.type == "supergroup")
router.message.filter(F.chat.type == "supergroup")


async def on_startup(dispatcher: Dispatcher):
   print('Bot on')
   redis = Redis(host="localhost", port=6379, db=0) 
   antiflood_middleware = AntiFloodMiddleware(redis=redis)
   router.message.middleware(antiflood_middleware)
   router_user.message.middleware(antiflood_middleware)
   router_admin.message.middleware(antiflood_middleware)
   router_messages.message.middleware(antiflood_middleware)
   router_congat.message.middleware(antiflood_middleware)
   router_profinity.message.middleware(antiflood_middleware)
   print("Anti-flood middleware has been set up.")

async def main():
    dp = Dispatcher()
    dp.include_router(router_congat)
    dp.include_router(router_admin)
    dp.include_router(router_user)
    dp.include_router(router_profinity)
    dp.include_router(router_messages)
    dp.include_router(router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
      asyncio.run(main())
    except KeyboardInterrupt:
       print('Bot off')