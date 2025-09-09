import asyncio
import redis.asyncio as redis
from collections import defaultdict

from bot.ai_bot import AIBot
from services.waha import Waha
from services.memory import clear_session_history, get_session_messages
from exceptions.exceptions import (
    BufferException,
    MemoryException,
    ConfigurationException
)
from config.config import Config

if not Config.REDIS_URL:
    raise ConfigurationException("REDIS_URL is not configured")

if Config.DEBOUNCE_SECONDS <= 0:
    raise ConfigurationException(f"DEBOUNCE_SECONDS must be positive, got {Config.DEBOUNCE_SECONDS}")

if Config.BUFFER_TTL <= 0:
    raise ConfigurationException(f"BUFFER_TTL must be positive, got {Config.BUFFER_TTL}")

try:
    redis_client = redis.Redis.from_url(Config.REDIS_URL, decode_responses=True)
except Exception as e:
    raise ConfigurationException(f"Failed to create Redis client: {str(e)}")

debounce_tasks = defaultdict(asyncio.Task)


async def buffer_message(chat_id: str, message: str):
    try:
        if not chat_id:
            raise BufferException("Chat ID cannot be empty")

        if not message:
            raise BufferException("Message cannot be empty")

    except BufferException:
        raise
    except Exception as e:
        raise BufferException(f"Error validating parameters: {str(e)}")

    try:
        buffer_key = f'{chat_id}{Config.BUFFER_KEY_SUFIX}'

        await redis_client.rpush(buffer_key, message)
        await redis_client.expire(buffer_key, Config.BUFFER_TTL)

        print(f'[BUFFER] Message added to buffer for {chat_id}: {message}')

        if debounce_tasks.get(chat_id):
            debounce_tasks[chat_id].cancel()
            print(f'[BUFFER] Debounce reset for {chat_id}')

        debounce_tasks[chat_id] = asyncio.create_task(handle_debounce(chat_id))

    except Exception as e:
        raise BufferException(f"Failed to buffer message for {chat_id}: {str(e)}") from e


async def handle_debounce(chat_id: str):
    try:
        print(f'[BUFFER] Starting debounce for {chat_id}')
        await asyncio.sleep(float(Config.DEBOUNCE_SECONDS))

        buffer_key = f'{chat_id}{Config.BUFFER_KEY_SUFIX}'
        messages = await redis_client.lrange(buffer_key, 0, -1)

        full_message = ' '.join(messages).strip()

        if full_message:
            print(f'[BUFFER] Sending grouped message to {chat_id}: {full_message}')

            try:
                waha = Waha()
                ai_bot = AIBot()

                await asyncio.to_thread(waha.start_typing, chat_id=chat_id)

                # History is automatically managed by Redis
                response_message = await asyncio.to_thread(
                    ai_bot.get_response,
                    question=full_message,
                    session_id=chat_id,  # Uses chat_id as session_id for Redis
                )

                await asyncio.gather(
                    asyncio.to_thread(waha.send_message, chat_id=chat_id, message=response_message),
                    asyncio.to_thread(waha.stop_typing, chat_id=chat_id)
                )

                print(f'[BUFFER] Response sent to {chat_id}: {response_message}')

            except Exception as e:
                raise BufferException(f"Error processing AI response for {chat_id}: {str(e)}") from e

        await redis_client.delete(buffer_key)

    except asyncio.CancelledError:
        print(f'[BUFFER] Debounce cancelled for {chat_id}')
        raise
    except BufferException:
        raise
    except Exception as e:
        raise BufferException(f"Error in debounce for {chat_id}: {str(e)}") from e


async def cleanup_expired_tasks():
    try:
        expired_tasks = []
        for chat_id, task in debounce_tasks.items():
            if task.done():
                expired_tasks.append(chat_id)

        for chat_id in expired_tasks:
            del debounce_tasks[chat_id]
            print(f'[BUFFER] Debounce task removed for {chat_id}')

    except Exception as e:
        raise BufferException(f"Error cleaning up expired tasks: {str(e)}") from e


async def get_buffer_status(chat_id: str):
    try:
        if not chat_id:
            raise BufferException("Chat ID cannot be empty")

    except BufferException:
        raise
    except Exception as e:
        raise BufferException(f"Error validating chat_id: {str(e)}")

    try:
        buffer_key = f'{chat_id}{Config.BUFFER_KEY_SUFIX}'
        messages = await redis_client.lrange(buffer_key, 0, -1)
        ttl = await redis_client.ttl(buffer_key)

        return {
            'chat_id': chat_id,
            'messages_count': len(messages),
            'messages': messages,
            'ttl': ttl,
            'has_pending_debounce': chat_id in debounce_tasks
        }

    except Exception as e:
        raise BufferException(f"Failed to get buffer status for {chat_id}: {str(e)}") from e


async def clear_chat_history(chat_id: str):
    try:
        if not chat_id:
            raise BufferException("Chat ID cannot be empty")

    except BufferException:
        raise
    except Exception as e:
        raise BufferException(f"Error validating chat_id: {str(e)}")

    try:
        clear_session_history(chat_id)
        print(f'[BUFFER] History cleared for {chat_id}')
        return {'status': 'success', 'message': f'History cleared for {chat_id}'}

    except (MemoryException, ConfigurationException) as e:
        raise BufferException(f"Error clearing history for {chat_id}: {str(e)}") from e
    except Exception as e:
        raise BufferException(f"Unexpected error clearing history for {chat_id}: {str(e)}") from e


async def get_chat_history(chat_id: str, limit: int = 10):
    try:
        if not chat_id:
            raise BufferException("Chat ID cannot be empty")

        if limit < 0:
            raise BufferException(f"Limit must be non-negative, got {limit}")

    except BufferException:
        raise
    except Exception as e:
        raise BufferException(f"Error validating parameters: {str(e)}")

    try:
        messages = get_session_messages(chat_id, limit)
        formatted_messages = []

        for msg in messages:
            if hasattr(msg, 'content'):
                msg_type = 'user' if msg.__class__.__name__ == 'HumanMessage' else 'assistant'
                formatted_messages.append({
                    'role': msg_type,
                    'content': msg.content,
                    'timestamp': getattr(msg, 'additional_kwargs', {}).get('timestamp', None)
                })

        return {
            'status': 'success',
            'chat_id': chat_id,
            'messages': formatted_messages,
            'total_messages': len(formatted_messages)
        }

    except (MemoryException, ConfigurationException) as e:
        raise BufferException(f"Error getting history for {chat_id}: {str(e)}") from e
    except Exception as e:
        raise BufferException(f"Unexpected error getting history for {chat_id}: {str(e)}") from e
