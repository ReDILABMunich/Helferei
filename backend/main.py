from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai import askAI

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://helferei-ashy.vercel.app",
        "https://helferei-git-frontend-salim-oseis-projects.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    answer: str


@app.get("/")
def root():
    return {"message": "Hello from Helferei Backend"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer = askAI(request.prompt)
    return ChatResponse(answer=answer)