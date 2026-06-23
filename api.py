import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from brain import process_concept

app = FastAPI()

# Mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_landing():
    return FileResponse("static/indexland.html")

@app.get("/app")
async def read_app():
    return FileResponse("static/app.html")

class RequestData(BaseModel):
    text: str

@app.post("/explain")
def explain_text(data: RequestData):
    return {"result": process_concept(data.text)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)