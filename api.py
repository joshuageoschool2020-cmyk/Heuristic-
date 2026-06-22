import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from brain import process_concept
import uvicorn

# 1. Initialize app FIRST
app = FastAPI()

# 2. Define absolute path to ensure Render finds your files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 3. Routes
@app.get("/")
async def read_landing():
    return FileResponse(os.path.join(BASE_DIR, 'indexland.html'))

@app.get("/app")
async def read_app():
    return FileResponse(os.path.join(BASE_DIR, 'app.html'))

# 4. API logic
class RequestData(BaseModel):
    text: str

@app.post("/explain")
def explain_text(data: RequestData):
    result = process_concept(data.text)
    return {"result": result}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)