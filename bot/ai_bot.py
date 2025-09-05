from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from services.memory import get_session_history, trim_history_if_needed

from core.config import Config

Config.setup_environment()

class AIBot:
    def __init__(self):
        self.__model = Config.OPENAI_MODEL
        self.__temperature = Config.OPENAI_TEMPERATURE
        self.__retriever = self.__build_retriever()
        self.__chain = self.__build_chain()

    def __build_retriever(self):
        persist_directory = Config.CHROMA_PERSIST_DIR

        embedding = OpenAIEmbeddings(
            model=Config.OPENAI_EMBEDDING_MODEL,
            openai_api_key=Config.OPENAI_API_KEY
        )

        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding,
        )

        return vector_store.as_retriever(
            search_kwargs={'k': Config.RAG_SEARCH_K},
        )

    def __build_messages(self, history_messages, question):
        messages = []
        for message in history_messages:
            message_class = HumanMessage if message.get('fromMe') else AIMessage
            messages.append(message_class(content=message.get('body')))
        messages.append(HumanMessage(content=question))
        return messages

    def __build_chain(self):
        system_template = """You are a helpful AI assistant that answers questions based on the provided context and conversation history.
        Always respond in Brazilian Portuguese.

        Use the following pieces of context and the conversation history to answer the user's question.
        If you don't know the answer based on the context and history, say that you don't know.

        Context: {context}"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])

        llm = ChatOpenAI(
            model=self.__model,
            temperature=self.__temperature,
        )

        document_chain = create_stuff_documents_chain(llm, prompt)
        return document_chain

    def get_response(self, question, session_id=None):
        if session_id:
            try:
                redis_history = get_session_history(session_id)
                formatted_history = redis_history.messages
            except Exception as e:
                print(f"Error loading history from Redis: {e}")
                formatted_history = []
        else:
            formatted_history = []

        docs = self.__retriever.invoke(question)

        response = self.__chain.invoke({
            "input": question,
            "context": docs,
            "chat_history": formatted_history
        })

        if session_id:
            try:
                redis_history = get_session_history(session_id)
                redis_history.add_user_message(question)
                redis_history.add_ai_message(response)
                trim_history_if_needed(session_id)
            except Exception as e:
                print(f"Error saving history to Redis: {e}")

        return response
