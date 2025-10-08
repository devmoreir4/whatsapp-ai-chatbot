from decouple import config
from exceptions.exceptions import ConfigurationException


class Config:

    # OpenAI
    OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
    OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4o-mini')
    OPENAI_TEMPERATURE = config('OPENAI_TEMPERATURE', default=0.7, cast=float)
    OPENAI_EMBEDDING_MODEL = 'text-embedding-3-small'

    # RAG
    RAG_SEARCH_K = 30
    RAG_CHUNK_SIZE = 1000
    RAG_CHUNK_OVERLAP = 200
    RAG_DATA_DIR = '/app/data/documents'
    CHROMA_PERSIST_DIR = '/app/data/chroma_data'

    # Waha
    WAHA_API_URL = 'http://waha:3000'
    WAHA_SESSION = 'default'

    # Redis
    REDIS_URL = 'redis://redis:6379'
    BUFFER_KEY_SUFIX = ':buffer'
    DEBOUNCE_SECONDS = 10
    BUFFER_TTL = 300
    MAX_HISTORY_MESSAGES = 100
    HISTORY_TTL_HOURS = 168  # 7 days

    @classmethod
    def validate(cls):
        required_configs = [
            ('OPENAI_API_KEY', cls.OPENAI_API_KEY),
        ]

        missing = []
        for name, value in required_configs:
            if not value:
                missing.append(name)

        if missing:
            raise ConfigurationException(f"Missing required configs: {', '.join(missing)}")

        if cls.OPENAI_TEMPERATURE < 0 or cls.OPENAI_TEMPERATURE > 2:
            raise ConfigurationException(f"OPENAI_TEMPERATURE must be between 0 and 2, got {cls.OPENAI_TEMPERATURE}")

    @classmethod
    def setup_environment(cls):
        import os
        os.environ['OPENAI_API_KEY'] = cls.OPENAI_API_KEY
