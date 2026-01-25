from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from backend.services.rag_engine import RagEngine
from pydantic import BaseModel

router = APIRouter()

rag_engine = RagEngine()

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_EXTENSIONS = {"pdf"}

class QueryRequest(BaseModel):
    question: str

def validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file name")
    
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Only PDFs are accepted. You uploaded: {file_extension}"
        )
    
    if file.size and file.size > MAX_FILE_SIZE:
        size_mb = file.size / (1024 * 1024)
        max_mb = MAX_FILE_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=400, 
            detail=f"File too large ({size_mb:.1f}MB). Maximum size: {max_mb:.0f}MB"
        )

@router.get("/")
def read_root():
    return {"message": "API is working!"}

@router.post("/upload")
def upload_file(file: UploadFile = File(...)):
    
    validate_file(file)
    
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