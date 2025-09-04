import asyncio
from fastapi import FastAPI, Request, HTTPException
from decouple import config
import uvicorn

from services.message_buffer import buffer_message, cleanup_expired_tasks, get_buffer_status


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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting buffer status: {str(e)}")


@app.post('/buffer/cleanup')
async def cleanup_buffer():
    try:
        await cleanup_expired_tasks()
        return {'status': 'success', 'message': 'Expired tasks cleaned up'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up tasks: {str(e)}")


if __name__ == '__main__':
    debug = config('API_DEBUG', default=False, cast=bool)
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="debug" if debug else "info")
