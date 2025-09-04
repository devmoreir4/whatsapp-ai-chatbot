import asyncio
import redis.asyncio as redis
from collections import defaultdict
from decouple import config

from bot.ai_bot import AIBot
from services.waha import Waha


REDIS_URL = config('REDIS_URL', default='redis://redis:6379')
BUFFER_KEY_SUFIX = config('BUFFER_KEY_SUFIX', default=':buffer')
DEBOUNCE_SECONDS = config('DEBOUNCE_SECONDS', default=10, cast=int)
BUFFER_TTL = config('BUFFER_TTL', default=300, cast=int)

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

debounce_tasks = defaultdict(asyncio.Task)


def log(*args):
    print('[BUFFER]', *args)


async def buffer_message(chat_id: str, message: str):
    buffer_key = f'{chat_id}{BUFFER_KEY_SUFIX}'

    await redis_client.rpush(buffer_key, message)
    await redis_client.expire(buffer_key, BUFFER_TTL)

    log(f'Message added to buffer for {chat_id}: {message}')

    if debounce_tasks.get(chat_id):
        debounce_tasks[chat_id].cancel()
        log(f'Debounce reset for {chat_id}')

    debounce_tasks[chat_id] = asyncio.create_task(handle_debounce(chat_id))


async def handle_debounce(chat_id: str):
    try:
        log(f'Starting debounce for {chat_id}')
        await asyncio.sleep(float(DEBOUNCE_SECONDS))

        buffer_key = f'{chat_id}{BUFFER_KEY_SUFIX}'
        messages = await redis_client.lrange(buffer_key, 0, -1)

        full_message = ' '.join(messages).strip()

        if full_message:
            log(f'Sending grouped message to {chat_id}: {full_message}')

            waha = Waha()
            ai_bot = AIBot()

            await asyncio.to_thread(waha.start_typing, chat_id=chat_id)

            history_limit = config('HISTORY_LIMIT', default=10, cast=int)
            history_messages = await asyncio.to_thread(
                waha.get_history_messages,
                chat_id=chat_id,
                limit=history_limit,
            )

            response_message = await asyncio.to_thread(
                ai_bot.get_response,
                question=full_message,
                chat_history=history_messages,
            )

            await asyncio.gather(
                asyncio.to_thread(waha.send_message, chat_id=chat_id, message=response_message),
                asyncio.to_thread(waha.stop_typing, chat_id=chat_id)
            )

            log(f'Response sent to {chat_id}: {response_message}')

        await redis_client.delete(buffer_key)

    except asyncio.CancelledError:
        log(f'Debounce cancelled for {chat_id}')
    except Exception as e:
        log(f'Error in debounce for {chat_id}: {e}')


async def cleanup_expired_tasks():
    expired_tasks = []
    for chat_id, task in debounce_tasks.items():
        if task.done():
            expired_tasks.append(chat_id)

    for chat_id in expired_tasks:
        del debounce_tasks[chat_id]
        log(f'Debounce task removed for {chat_id}')


async def get_buffer_status(chat_id: str):
    buffer_key = f'{chat_id}{BUFFER_KEY_SUFIX}'
    messages = await redis_client.lrange(buffer_key, 0, -1)
    ttl = await redis_client.ttl(buffer_key)

    return {
        'chat_id': chat_id,
        'messages_count': len(messages),
        'messages': messages,
        'ttl': ttl,
        'has_pending_debounce': chat_id in debounce_tasks
    }
