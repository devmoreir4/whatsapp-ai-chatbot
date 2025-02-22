import os
from decouple import config

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings


os.environ['HUGGINGFACE_API_KEY'] = config('HUGGINGFACE_API_KEY')


if __name__ == '__main__':
    pdf_file_path = '/app/rag/data/guidelines.pdf'
    pdf_loader = PyPDFLoader(pdf_file_path)
    pdf_docs = pdf_loader.load()

    csv_file_path = '/app/rag/data/river_data.csv'
    csv_loader = CSVLoader(file_path=csv_file_path)
    csv_docs = csv_loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    pdf_chunks = text_splitter.split_documents(pdf_docs)
    csv_chunks = text_splitter.split_documents(csv_docs)

    persist_directory = '/app/chroma_data'

    embedding = HuggingFaceEmbeddings()
    vector_store = Chroma(
        embedding_function=embedding,
        persist_directory=persist_directory,
    )

    vector_store.add_documents(documents=pdf_chunks + csv_chunks)
