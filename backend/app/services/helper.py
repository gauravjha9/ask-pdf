import shutil
from tempfile import NamedTemporaryFile
from fastapi import UploadFile
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain.schema import BaseRetriever

from app.services.llm import llm
from app.services.embedder import embedding_model

# Create prompt template
qa_prompt = PromptTemplate(
    template="""
      You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.

      {context}
      Question: {question}
    """,
    input_variables=["context", "question"]
)

def save_upload_to_temp_file(file: UploadFile, suffix=".pdf") -> str:
    """
    Saves an UploadFile to a temporary file and returns the file path.
    """
    with NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        return temp_file.name

def load_pdf_and_split(file_path: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """Loads a PDF and splits it into text chunks."""
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_documents(documents)

def create_vector_store(doc_chunks):
    """Creates and returns a FAISS vector store from document chunks."""
    return FAISS.from_documents(doc_chunks, embedding_model)

def build_retriever(file_path: str):
    """Loads and processes PDF, returning a retriever."""
    chunks = load_pdf_and_split(file_path)
    vector_store = create_vector_store(chunks)
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

def build_context_from_docs(retrieved_docs):
    return "\n\n".join(
        f"[Page {doc.metadata.get('page_label', doc.metadata.get('page', 'N/A'))} | "
        f"Title: {doc.metadata.get('title', 'Unknown Title')} | "
        f"Author: {doc.metadata.get('author', 'Unknown Author')} | "
        f"Total Pages: {doc.metadata.get('total_pages', 'N/A')}]\n\n"
        f"{doc.page_content}"
        for doc in retrieved_docs
    )
    
def generate_answer(retriever, question: str):
    """Generates an answer to the question based on retrieved context."""
    retrieved_docs = retriever.invoke(question)
    context_text = build_context_from_docs(retrieved_docs)
    prompt_input = qa_prompt.invoke({"context": context_text, "question": question})
    response = llm.invoke(prompt_input)
    return response.content