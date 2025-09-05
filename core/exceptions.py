class WhatsAppAIChatbotException(Exception):
    """Base exception for WhatsApp AI Chatbot"""
    pass


class RAGException(WhatsAppAIChatbotException):
    """Exception raised for RAG-related errors"""
    pass


class DocumentLoadException(RAGException):
    """Exception raised when document loading fails"""
    pass


class VectorStoreException(RAGException):
    """Exception raised when vector store operations fail"""
    pass


class EmbeddingException(RAGException):
    """Exception raised when embedding operations fail"""
    pass


class MemoryException(WhatsAppAIChatbotException):
    """Exception raised for memory/history-related errors"""
    pass


class BufferException(WhatsAppAIChatbotException):
    """Exception raised for message buffer-related errors"""
    pass


class ConfigurationException(WhatsAppAIChatbotException):
    """Exception raised for configuration-related errors"""
    pass


class WahaException(WhatsAppAIChatbotException):
    """Exception raised for WAHA API-related errors"""
    pass
