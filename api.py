import os
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def debug():
    # This will list the folder contents AND tell us the path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(current_dir)
    return {
        "current_directory": current_dir,
        "files_found": files
    }