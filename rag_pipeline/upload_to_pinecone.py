import os
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone

# Load .env from backend directory
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(env_path)

def upload_vectors_to_pinecone():
    # Get credentials
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "paf")

    if not api_key:
        raise ValueError("PINECONE_API_KEY not set in .env")

    print(f"Connecting to Pinecone...")
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)

    # Load PDF chunks
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    pdf_path = Path(__file__).parent / "AcharyaPrashantBook.pdf"

    print(f"Loading PDF: {pdf_path}")
    loader = PyPDFLoader(str(pdf_path))
    documents = loader.load()

    print("Splitting documents...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    # Upload to Pinecone using Pinecone's Inference API for embeddings
    print("Uploading vectors to Pinecone (using Pinecone Inference API)...")
    batch_size = 50

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        vectors_to_upload = []

        # Extract text from batch
        texts = [chunk.page_content for chunk in batch]

        # Generate embeddings via Pinecone Inference API
        res = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=texts,
            parameters={"input_type": "passage"}
        )

        # Create vector records
        for j, embedding_obj in enumerate(res.data):
            vector_id = f"doc_{i+j}"
            vectors_to_upload.append({
                "id": vector_id,
                "values": embedding_obj.values,
                "metadata": {"text": texts[j]}
            })

        # Upsert to Pinecone
        index.upsert(vectors=vectors_to_upload)
        print(f"Uploaded batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")

    print(f"\n[OK] Successfully uploaded {len(chunks)} vectors to Pinecone!")
    print(f"[OK] Index: {index_name}")
    print(f"[OK] Embedding model: multilingual-e5-large")

if __name__ == "__main__":
    upload_vectors_to_pinecone()
