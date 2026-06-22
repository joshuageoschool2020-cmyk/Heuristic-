import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from brain import process_concept
import uvicorn

app = FastAPI()

# Get the directory where api.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
async def read_landing():
    return FileResponse(os.path.join(BASE_DIR, 'indexland.html'))

@app.get("/app")
async def read_app():
    return FileResponse(os.path.join(BASE_DIR, 'app.html'))

class RequestData(BaseModel):
    text: str

@app.post("/explain")
def explain_text(data: RequestData):
    result = process_concept(data.text)
    return {"result": result}