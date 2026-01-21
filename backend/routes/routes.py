from fastapi import APIRouter, UploadFile, File
import shutil
import os
from backend.services.rag_engine import RagEngine
from pydantic import BaseModel

router = APIRouter()

rag_engine = RagEngine()

class QueryRequest(BaseModel):
    question: str

@router.get("/")
def read_root():
    return {"message": "API is working!"}

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):

    os.makedirs("temp", exist_ok=True)

    file_path = f"temp/{file.filename}"

    # wb don't try to transform binary in text like 'w'
    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    rag_engine.process_document(file_path)

    return {"filename": file.filename, "status": "Processed!"}

@router.post("/chat")
def chat_pdf(request: QueryRequest):

    answer = rag_engine.answer(request.question)

    return {
        "question": request.question,
        "answer": answer
    }