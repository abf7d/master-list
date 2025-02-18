

## main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryInput(BaseModel):
    text: str
    model_name: Optional[str] = "gpt-3.5-turbo"
    
@app.get("/")
async def root():
    return {"message": "AI Backend API is running"}

@app.post("/api/query")
async def process_query(query_input: QueryInput):
    # This is where you'll add your LangChain/LLM logic later
    return {
        "response": f"Processed query: {query_input.text}",
        "model_used": query_input.model_name
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)