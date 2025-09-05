from decouple import config
from exceptions import ConfigurationException


class Config:

    # OpenAI
    OPENAI_API_KEY = config('OPENAI_API_KEY')
    OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-3.5-turbo')
    OPENAI_TEMPERATURE = config('OPENAI_TEMPERATURE', default=0.7, cast=float)
    OPENAI_EMBEDDING_MODEL = config('OPENAI_EMBEDDING_MODEL', default='text-embedding-3-small')

    # RAG
    RAG_SEARCH_K = config('RAG_SEARCH_K', default=30, cast=int)
    RAG_CHUNK_SIZE = config('RAG_CHUNK_SIZE', default=1000, cast=int)
    RAG_CHUNK_OVERLAP = config('RAG_CHUNK_OVERLAP', default=200, cast=int)
    RAG_DATA_DIR = config('RAG_DATA_DIR', default='/app/rag/data')
    CHROMA_PERSIST_DIR = config('CHROMA_PERSIST_DIR', default='/app/chroma_data')

    # Waha
    WAHA_API_URL = config('WAHA_API_URL', default='http://waha:3000')
    WAHA_SESSION = config('WAHA_SESSION', default='default')

    # Redis
    REDIS_URL = config('REDIS_URL', default='redis://redis:6379')
    BUFFER_KEY_SUFIX = config('BUFFER_KEY_SUFIX', default=':buffer')
    DEBOUNCE_SECONDS = config('DEBOUNCE_SECONDS', default=10, cast=int)
    BUFFER_TTL = config('BUFFER_TTL', default=300, cast=int)
    MAX_HISTORY_MESSAGES = config('MAX_HISTORY_MESSAGES', default=100, cast=int)
    HISTORY_TTL_HOURS = config('HISTORY_TTL_HOURS', default=168, cast=int)  # 7 days

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

        if cls.DEBOUNCE_SECONDS <= 0:
            raise ConfigurationException(f"DEBOUNCE_SECONDS must be positive, got {cls.DEBOUNCE_SECONDS}")

        if cls.BUFFER_TTL <= 0:
            raise ConfigurationException(f"BUFFER_TTL must be positive, got {cls.BUFFER_TTL}")

        if cls.MAX_HISTORY_MESSAGES <= 0:
            raise ConfigurationException(f"MAX_HISTORY_MESSAGES must be positive, got {cls.MAX_HISTORY_MESSAGES}")

        if cls.HISTORY_TTL_HOURS <= 0:
            raise ConfigurationException(f"HISTORY_TTL_HOURS must be positive, got {cls.HISTORY_TTL_HOURS}")

        if cls.RAG_SEARCH_K <= 0:
            raise ConfigurationException(f"RAG_SEARCH_K must be positive, got {cls.RAG_SEARCH_K}")

        if cls.RAG_CHUNK_SIZE <= 0:
            raise ConfigurationException(f"RAG_CHUNK_SIZE must be positive, got {cls.RAG_CHUNK_SIZE}")

        if cls.RAG_CHUNK_OVERLAP < 0:
            raise ConfigurationException(f"RAG_CHUNK_OVERLAP must be non-negative, got {cls.RAG_CHUNK_OVERLAP}")

        if cls.OPENAI_TEMPERATURE < 0 or cls.OPENAI_TEMPERATURE > 2:
            raise ConfigurationException(f"OPENAI_TEMPERATURE must be between 0 and 2, got {cls.OPENAI_TEMPERATURE}")

    @classmethod
    def setup_environment(cls):
        import os
        os.environ['OPENAI_API_KEY'] = cls.OPENAI_API_KEY
