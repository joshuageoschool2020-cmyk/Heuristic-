import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from brain import process_concept
import uvicorn

app = FastAPI()

# Routes now correctly use the 'app' object defined above
@app.get("/")
async def read_landing():
    return FileResponse(os.path.join(os.getcwd(), 'indexland.html'))

@app.get("/app")
async def read_app():
    return FileResponse(os.path.join(os.getcwd(), 'app.html'))

class RequestData(BaseModel):
    text: str

@app.post("/explain")
def explain_text(data: RequestData):
    result = process_concept(data.text)
    return {"result": result}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)