import os

from decouple import config

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings

os.environ['OPENAI_API_KEY'] = config('OPENAI_API_KEY')

class AIBot:
    def __init__(self):
        self.__model = config('OPENAI_MODEL', default='gpt-3.5-turbo')
        self.__temperature = config('OPENAI_TEMPERATURE', default=0.7, cast=float)
        self.__retriever = self.__build_retriever()
        self.__chain = self.__build_chain()

    def __build_retriever(self):
        persist_directory = config('CHROMA_PERSIST_DIR', default='/app/chroma_data')

        embedding_model = config('OPENAI_EMBEDDING_MODEL', default='text-embedding-3-small')
        embedding = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=config('OPENAI_API_KEY')
        )

        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding,
        )

        search_k = config('RAG_SEARCH_K', default=30, cast=int)
        return vector_store.as_retriever(
            search_kwargs={'k': search_k},
        )

    def __build_messages(self, history_messages, question):
        messages = []
        for message in history_messages:
            message_class = HumanMessage if message.get('fromMe') else AIMessage
            messages.append(message_class(content=message.get('body')))
        messages.append(HumanMessage(content=question))
        return messages

    def __build_chain(self):
        system_template = """You are a helpful AI assistant that answers questions based on the provided context.
        Always respond in Brazilian Portuguese.

        Use the following pieces of context to answer the user's question.
        If you don't know the answer based on the context, say that you don't know.

        Context: {context}

        Question: {input}"""

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

    def get_response(self, question, chat_history=None):
        if chat_history is None:
            chat_history = []

        formatted_history = []
        for message in chat_history:
            if message.get('role') == 'user':
                formatted_history.append(HumanMessage(content=message.get('content', '')))
            elif message.get('role') == 'assistant':
                formatted_history.append(AIMessage(content=message.get('content', '')))

        docs = self.__retriever.invoke(question)

        response = self.__chain.invoke({
            "input": question,
            "context": docs,
            "chat_history": formatted_history
        })

        return response
