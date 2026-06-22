import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()

# Mount the 'static' folder to make all files inside it accessible
# This ensures Tailwind and other styles are loaded correctly
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_landing():
    # Points to the new location in the static folder
    return FileResponse("static/indexland.html")

@app.get("/app")
async def read_app():
    # Points to the new location in the static folder
    return FileResponse("static/app.html")

# Keep your existing logic
class RequestData(from pydantic import BaseModel):
    text: str

# Import your brain logic
from brain import process_concept

@app.post("/explain")
def explain_text(data: RequestData):
    return {"result": process_concept(data.text)}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)