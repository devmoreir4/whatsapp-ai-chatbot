from fastapi import FastAPI, Request, HTTPException
import uvicorn

from services.message_buffer import buffer_message, cleanup_expired_tasks, get_buffer_status, clear_chat_history, get_chat_history
from services.memory import get_history_stats
from core.exceptions import (
    WhatsAppAIChatbotException,
    RAGException,
    MemoryException,
    BufferException,
    ConfigurationException,
    WahaException
)
from core.config import Config

Config.validate()


app = FastAPI(title="WhatsApp AI Chatbot", version="1.0.0")


@app.post('/chatbot/webhook/')
async def webhook(request: Request):
    try:
        data = await request.json()
        chat_id = data['payload']['from']
        received_message = data['payload']['body']
        is_group = '@g.us' in chat_id

        if is_group:
            return {'status': 'success', 'message': 'Group message ignored.'}

        await buffer_message(chat_id, received_message)

        return {'status': 'success', 'message': 'Message buffered for debounce'}

    except (WhatsAppAIChatbotException, WahaException) as e:
        raise HTTPException(status_code=400, detail=f"Application error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get('/health')
async def health_check():
    return {'status': 'healthy', 'service': 'whatsapp-ai-chatbot'}


@app.get('/buffer/status/{chat_id}')
async def get_buffer_status_endpoint(chat_id: str):
    try:
        status = await get_buffer_status(chat_id)
        return status
    except BufferException as e:
        raise HTTPException(status_code=400, detail=f"Buffer error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting buffer status: {str(e)}")


@app.post('/buffer/cleanup')
async def cleanup_buffer():
    try:
        await cleanup_expired_tasks()
        return {'status': 'success', 'message': 'Expired tasks cleaned up'}
    except BufferException as e:
        raise HTTPException(status_code=400, detail=f"Buffer cleanup error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up tasks: {str(e)}")


@app.delete('/chat/history/{chat_id}')
async def clear_history(chat_id: str):
    try:
        result = await clear_chat_history(chat_id)
        if result['status'] == 'success':
            return result
        else:
            raise HTTPException(status_code=500, detail=result['message'])
    except MemoryException as e:
        raise HTTPException(status_code=400, detail=f"Memory error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing chat history: {str(e)}")


@app.get('/chat/history/{chat_id}')
async def get_history(chat_id: str, limit: int = 10):
    try:
        result = await get_chat_history(chat_id, limit)
        if result['status'] == 'success':
            return result
        else:
            raise HTTPException(status_code=500, detail=result['message'])
    except MemoryException as e:
        raise HTTPException(status_code=400, detail=f"Memory error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat history: {str(e)}")


@app.get('/chat/history/{chat_id}/stats')
async def get_history_stats_endpoint(chat_id: str):
    try:
        stats = get_history_stats(chat_id)
        return stats
    except MemoryException as e:
        raise HTTPException(status_code=400, detail=f"Memory error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting history stats: {str(e)}")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
