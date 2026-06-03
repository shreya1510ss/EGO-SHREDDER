import os
import shutil
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer

def build_pdf_vectorstore():
    pdf_path = Path(__file__).parent / "AcharyaPrashantBook.pdf"
    db_path = Path(__file__).parent.parent / "ego_shredder_db"

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    print(f"Loading PDF from: {pdf_path}")
    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()
    print(f"Loaded {len(documents)} pages from PDF")

    print("Splitting documents into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    print("Initializing sentence-transformers embeddings (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    class SentenceTransformersEmbedding:
        def __init__(self, model):
            self.model = model
        def embed_documents(self, texts):
            return self.model.encode(texts, convert_to_numpy=True).tolist()
        def embed_query(self, text):
            return self.model.encode(text, convert_to_numpy=True).tolist()

    embeddings = SentenceTransformersEmbedding(model)

    if db_path.exists():
        print(f"Removing existing vector store from: {db_path}")
        shutil.rmtree(db_path)

    print("Building FAISS vector store with real semantic embeddings...")
    vector_store = FAISS.from_documents(chunks, embeddings)

    db_path.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(db_path))
    print(f"[OK] Vector store saved to: {db_path}")
    print(f"[OK] Stored {len(chunks)} chunks from PDF with real embeddings")
    print("Done!")

if __name__ == "__main__":
    build_pdf_vectorstore()
