from fastapi import FastAPI
from pydantic import BaseModel
from ai import askAI

app = FastAPI()

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