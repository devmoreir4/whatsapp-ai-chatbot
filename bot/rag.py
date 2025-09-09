import os
import glob

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

from exceptions.exceptions import (
    RAGException,
    DocumentLoadException,
    VectorStoreException,
    EmbeddingException,
    ConfigurationException
)
from config.config import Config

Config.setup_environment()


def load_documents_from_directory(data_directory=None):
    try:
        if data_directory is None:
            data_directory = Config.RAG_DATA_DIR

        if not os.path.exists(data_directory):
            raise ConfigurationException(f"Data directory does not exist: {data_directory}")

        if not os.path.isdir(data_directory):
            raise ConfigurationException(f"Path is not a directory: {data_directory}")

    except Exception as e:
        if isinstance(e, ConfigurationException):
            raise
        raise ConfigurationException(f"Error validating data directory: {str(e)}")

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
        try:
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
                    error_msg = f"Failed to load {file_path}: {str(e)}"
                    print(f"ERROR: {error_msg}")
                    raise DocumentLoadException(error_msg) from e

        except DocumentLoadException:
            # Re-raise DocumentLoadException
            raise
        except Exception as e:
            error_msg = f"Error processing {extension} files: {str(e)}"
            print(f"ERROR: {error_msg}")
            raise DocumentLoadException(error_msg) from e

    return all_documents


def create_vector_store(documents, persist_directory=None):
    try:
        if persist_directory is None:
            persist_directory = Config.CHROMA_PERSIST_DIR

        if not documents:
            raise VectorStoreException("No documents provided for vector store creation")

    except Exception as e:
        if isinstance(e, (ConfigurationException, VectorStoreException)):
            raise
        raise ConfigurationException(f"Error validating parameters: {str(e)}")

    try:
        print(f"Processing {len(documents)} documents...")

        chunk_size = Config.RAG_CHUNK_SIZE
        chunk_overlap = Config.RAG_CHUNK_OVERLAP

        if chunk_size <= 0:
            raise ConfigurationException(f"Invalid chunk_size: {chunk_size}. Must be positive.")
        if chunk_overlap < 0:
            raise ConfigurationException(f"Invalid chunk_overlap: {chunk_overlap}. Must be non-negative.")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} text chunks")

        if not chunks:
            raise VectorStoreException("No text chunks created from documents")

    except Exception as e:
        if isinstance(e, (ConfigurationException, VectorStoreException)):
            raise
        raise VectorStoreException(f"Error processing documents: {str(e)}") from e

    try:
        embedding_model = Config.OPENAI_EMBEDDING_MODEL
        openai_api_key = Config.OPENAI_API_KEY

        if not openai_api_key:
            raise ConfigurationException("OPENAI_API_KEY is not configured")

        embedding = OpenAIEmbeddings(
            model=embedding_model,
            openai_api_key=openai_api_key
        )

    except Exception as e:
        if isinstance(e, ConfigurationException):
            raise
        raise EmbeddingException(f"Error creating embedding model: {str(e)}") from e

    try:
        vector_store = Chroma(
            embedding_function=embedding,
            persist_directory=persist_directory,
        )

        vector_store.add_documents(documents=chunks)
        print(f"SUCCESS: Vector store created successfully at {persist_directory}")

        return vector_store

    except Exception as e:
        raise VectorStoreException(f"Error creating vector store: {str(e)}") from e


if __name__ == '__main__':
    try:
        print("Starting RAG indexing process...")

        documents = load_documents_from_directory()

        if not documents:
            print("ERROR: No documents found in /app/data/documents folder")
            exit(1)

        vector_store = create_vector_store(documents)

        print("SUCCESS: RAG indexing process completed successfully!")
        print(f"Total documents processed: {len(documents)}")
        print("Bot is ready to answer questions based on loaded documents!")

    except ConfigurationException as e:
        print(f"CONFIGURATION ERROR: {e}")
        exit(1)
    except DocumentLoadException as e:
        print(f"DOCUMENT LOAD ERROR: {e}")
        exit(1)
    except VectorStoreException as e:
        print(f"VECTOR STORE ERROR: {e}")
        exit(1)
    except EmbeddingException as e:
        print(f"EMBEDDING ERROR: {e}")
        exit(1)
    except RAGException as e:
        print(f"RAG ERROR: {e}")
        exit(1)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        exit(1)
