import os
import glob
from decouple import config

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredWordDocumentLoader
)
from langchain_openai import OpenAIEmbeddings


os.environ['OPENAI_API_KEY'] = config('OPENAI_API_KEY')


def load_documents_from_directory(data_directory=None):
    if data_directory is None:
        data_directory = config('RAG_DATA_DIR', default='/app/rag/data')
    all_documents = []

    loaders = {
        '.pdf': PyPDFLoader,
        '.csv': CSVLoader,
        '.txt': TextLoader,
        '.md': UnstructuredMarkdownLoader,
        '.docx': UnstructuredWordDocumentLoader,
        '.doc': UnstructuredWordDocumentLoader,
    }

    for extension, loader_class in loaders.items():
        pattern = os.path.join(data_directory, f'**/*{extension}')
        files = glob.glob(pattern, recursive=True)

        for file_path in files:
            try:
                print(f"Loading file: {file_path}")
                loader = loader_class(file_path)
                docs = loader.load()
                all_documents.extend(docs)
                print(f"SUCCESS: {file_path} loaded successfully ({len(docs)} documents)")
            except Exception as e:
                print(f"ERROR: Failed to load {file_path}: {e}")

    return all_documents


def create_vector_store(documents, persist_directory=None):
    if persist_directory is None:
        persist_directory = config('CHROMA_PERSIST_DIR', default='/app/chroma_data')

    print(f"Processing {len(documents)} documents...")

    chunk_size = config('RAG_CHUNK_SIZE', default=1000, cast=int)
    chunk_overlap = config('RAG_CHUNK_OVERLAP', default=200, cast=int)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks")

    embedding_model = config('OPENAI_EMBEDDING_MODEL', default='text-embedding-3-small')
    embedding = OpenAIEmbeddings(
        model=embedding_model,
        openai_api_key=config('OPENAI_API_KEY')
    )

    vector_store = Chroma(
        embedding_function=embedding,
        persist_directory=persist_directory,
    )

    vector_store.add_documents(documents=chunks)
    print(f"SUCCESS: Vector store created successfully at {persist_directory}")

    return vector_store


if __name__ == '__main__':
    print("Starting RAG indexing process...")

    documents = load_documents_from_directory()

    if not documents:
        print("ERROR: No documents found in /app/rag/data folder")
        print("Supported formats: PDF, CSV, TXT, MD, DOC, DOCX")
        exit(1)

    vector_store = create_vector_store(documents)

    print("SUCCESS: RAG indexing process completed successfully!")
    print(f"Total documents processed: {len(documents)}")
    print("Bot is ready to answer questions based on loaded documents!")
