import uuid
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.services.helper import load_pdf_and_split, create_vector_store, generate_answer, save_upload_to_temp_file

router = APIRouter(prefix="", tags=["PDF QA"])

# In-memory session store
session_vectorstores = {}

@router.post('/upload-file')
async def upload_pdf(file: UploadFile = File(...)):
    # Save uploaded PDF to a temporary file
    temp_file_path = save_upload_to_temp_file(file)

    # Process the PDF
    chunks = load_pdf_and_split(temp_file_path)
    vectorstore = create_vector_store(chunks)

    # Save vectorstore in session
    session_id = str(uuid.uuid4())
    session_vectorstores[session_id] = vectorstore

    return JSONResponse({"message": "PDF uploaded and processed", "session_id": session_id}, status_code=200)

@router.post('/query')
def get_answer_from_pdf(session_id: str = Form(...), query: str = Form(...)):
    if session_id not in session_vectorstores:
        return JSONResponse({"error": "Session not found or expired"}, status_code=404)

    vectorstore = session_vectorstores[session_id]
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    answer = generate_answer(retriever, query)
    return JSONResponse({"answer": answer}, status_code=200)
