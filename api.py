from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from brain import process_concept
import os
import uvicorn

app = FastAPI()

class RequestData(BaseModel):
    text: str

@app.get("/")
async def read_landing():
    return FileResponse('indexland.html')

@app.get("/app")
async def read_app():
    return FileResponse('app.html')

@app.post("/explain")
def explain_text(data: RequestData):
    # This calls your brain logic without any manual input
    result = process_concept(data.text)
    return {"result": result}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)