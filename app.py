from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
from model import query_rag

app = FastAPI()

# CORS for frontend-backend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

@app.post("/chat")
async def chat(query_request: Query):
    user_query = query_request.query.lower()
    response = query_rag(user_query)

    # Polite greeting if user says hello
    if re.search(r"\b(hi|hello|hey|salam|marhaba)\b", user_query):
        response = "Hello there! How can I assist you today?"

    return {"response": response}