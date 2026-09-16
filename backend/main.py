from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai import ask_ai

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

# class ChatRequest(BaseModel):
#     prompt: str

class ChatRequest(BaseModel):
    message: str
    previous_response_id: str | None = None

# class ChatResponse(BaseModel):
#     answer: str

class ChatResponse(BaseModel):
    answer: str
    response_id: str


@app.get("/")
def root():
    return {"message": "Hello from Helferei Backend, test rendering a branch"}

# @app.post("/chat", response_model=ChatResponse)
# def chat(request: ChatRequest):
#     answer = askAI(request.prompt)
#     return ChatResponse(answer=answer)

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    answer, response_id = ask_ai(request.message, request.previous_response_id,)

    return ChatResponse(answer=answer, response_id=response_id,)