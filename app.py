from fastapi import FastAPI
import uvicorn

from routes import router
from config.config import Config

Config.validate()

app = FastAPI(title="WhatsApp AI Chatbot", version="1.0.0")

app.include_router(router)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")
