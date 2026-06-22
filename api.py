from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from brain import process_concept

app = FastAPI()

# Routes to serve your HTML files
@app.get("/")
async def read_landing():
    return FileResponse('indexland.html')

@app.get("/app")
async def read_app():
    return FileResponse('app.html')

# API endpoint for the engine
class RequestData(BaseModel):
    text: str

@app.post("/explain")
def explain_text(data: RequestData):
    result = process_concept(data.text)
    return {"result": result}