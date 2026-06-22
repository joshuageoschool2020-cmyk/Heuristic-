import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()

# 1. Mount the entire root directory as static
# This allows the server to serve any file directly by its filename
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_landing():
    return FileResponse("indexland.html")

@app.get("/app")
async def read_app():
    return FileResponse("app.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)