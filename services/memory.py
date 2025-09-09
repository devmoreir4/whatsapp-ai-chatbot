from langchain_community.chat_message_histories import RedisChatMessageHistory

from exceptions.exceptions import (
    MemoryException,
    ConfigurationException
)
from config.config import Config


def get_session_history(session_id):
    try:
        if not session_id:
            raise ConfigurationException("Session ID cannot be empty")

        if not isinstance(session_id, str):
            raise ConfigurationException(f"Session ID must be a string, got {type(session_id)}")

        if Config.MAX_HISTORY_MESSAGES <= 0:
            raise ConfigurationException(f"MAX_HISTORY_MESSAGES must be positive, got {Config.MAX_HISTORY_MESSAGES}")

        if Config.HISTORY_TTL_HOURS <= 0:
            raise ConfigurationException(f"HISTORY_TTL_HOURS must be positive, got {Config.HISTORY_TTL_HOURS}")

        if not Config.REDIS_URL:
            raise ConfigurationException("REDIS_URL is not configured")

    except ConfigurationException:
        raise
    except Exception as e:
        raise ConfigurationException(f"Error validating parameters: {str(e)}")

    try:
        return RedisChatMessageHistory(
            session_id=session_id,
            url=Config.REDIS_URL,
            ttl=Config.HISTORY_TTL_HOURS * 3600,  # hours to seconds
        )
    except Exception as e:
        raise MemoryException(f"Failed to create Redis chat history for session {session_id}: {str(e)}") from e


def clear_session_history(session_id):
    try:
        history = get_session_history(session_id)
        history.clear()
    except (ConfigurationException, MemoryException):
        raise
    except Exception as e:
        raise MemoryException(f"Failed to clear history for session {session_id}: {str(e)}") from e


def get_session_messages(session_id, limit=None):
    try:
        if limit is not None and limit < 0:
            raise ConfigurationException(f"Limit must be non-negative, got {limit}")

    except ConfigurationException:
        raise
    except Exception as e:
        raise ConfigurationException(f"Error validating limit parameter: {str(e)}")

    try:
        history = get_session_history(session_id)
        messages = history.messages

        if limit:
            return messages[-limit:] if limit > 0 else messages

        return messages

    except (ConfigurationException, MemoryException):
        raise
    except Exception as e:
        raise MemoryException(f"Failed to get messages for session {session_id}: {str(e)}") from e


def trim_history_if_needed(session_id):
    try:
        history = get_session_history(session_id)
        messages = history.messages

        if len(messages) > Config.MAX_HISTORY_MESSAGES:
            # Keep only the most recent messages
            messages_to_keep = messages[-Config.MAX_HISTORY_MESSAGES:]
            history.clear()
            for msg in messages_to_keep:
                if msg.__class__.__name__ == 'HumanMessage':
                    history.add_user_message(msg.content)
                else:
                    history.add_ai_message(msg.content)
            print(f"History trimmed for {session_id}: {len(messages)} -> {len(messages_to_keep)} messages")

    except (ConfigurationException, MemoryException):
        raise
    except Exception as e:
        raise MemoryException(f"Failed to trim history for session {session_id}: {str(e)}") from e


def get_history_stats(session_id):
    try:
        history = get_session_history(session_id)
        messages = history.messages

        return {
            'session_id': session_id,
            'total_messages': len(messages),
            'max_allowed': Config.MAX_HISTORY_MESSAGES,
            'ttl_hours': Config.HISTORY_TTL_HOURS,
            'is_trimmed': len(messages) >= Config.MAX_HISTORY_MESSAGES
        }

    except (ConfigurationException, MemoryException):
        raise
    except Exception as e:
        raise MemoryException(f"Failed to get history stats for session {session_id}: {str(e)}") from e
