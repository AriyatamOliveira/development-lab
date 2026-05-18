from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uvicorn
from pydantic import BaseModel
from services.ingestion import process_pdf, process_youtube
from services.llm import generate_study_materials, chat_with_context

app = FastAPI(title="EduSpark Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    text_content: str
    material_type: str # "summary", "flashcards", "quiz"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    text_content: str
    message: str
    history: List[ChatMessage] = []

@app.post("/upload")
async def upload_document(
    file: Optional[UploadFile] = File(None),
    youtube_url: Optional[str] = Form(None),
    raw_text: Optional[str] = Form(None)
):
    try:
        content = ""
        if file:
            content = await process_pdf(file)
        elif youtube_url:
            content = process_youtube(youtube_url)
        elif raw_text:
            content = raw_text
        else:
            raise HTTPException(status_code=400, detail="No input provided")

        return {"status": "success", "content": content[:5000]} # Return prefix for processing
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate")
async def generate_material(req: GenerateRequest):
    try:
        result = await generate_study_materials(req.text_content, req.material_type)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        history_dicts = [{"role": m.role, "content": m.content} for m in req.history]
        result = await chat_with_context(req.text_content, req.message, history_dicts)
        return {"status": "success", "response": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
