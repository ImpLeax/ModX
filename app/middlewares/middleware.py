from aiogram import BaseMiddleware, types
from aiogram.types import ChatPermissions
from redis.asyncio import Redis
from typing import Any, Callable, Dict
from datetime import timedelta
import asyncio

class AntiFloodMiddleware(BaseMiddleware):
    def __init__(self, redis: Redis, limit: int = 5, period: int = 10):
        super().__init__()
        self.redis = redis
        self.limit = limit
        self.period = period

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, Dict[str, Any]], Any],
        event: types.TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, types.Message):
            user_id = event.from_user.id
            chat_id = event.chat.id
            redis_key = f"antiflood:{chat_id}:{user_id}"
            warn_key = f"antiflood_warned:{chat_id}:{user_id}"
            mute_time_key = f"mute_time:{chat_id}:{user_id}"

            messages = await self.redis.incr(redis_key)

            if messages == 1:
                await self.redis.expire(redis_key, self.period)

            if messages > self.limit:
                await event.delete()
                already_warned = await self.redis.exists(warn_key)

                if not already_warned:
                    await event.answer("⚠️ Please slow down. You are sending too many messages!")
                    await self.redis.setex(warn_key, self.period, 1)
                    await self.redis.setex(redis_key, self.period, 1)
                else:
                    await self.redis.setex(mute_time_key, self.period, 60)
                    await event.chat.restrict(
                        user_id=user_id,
                        permissions=ChatPermissions(can_send_messages=False),
                        until_date=timedelta(seconds=60)
                    )
                    await self.redis.delete(redis_key)
                    await self.redis.delete(warn_key)
            else:
                return await handler(event, data)
        else:
            return await handler(event, data)