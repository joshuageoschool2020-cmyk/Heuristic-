from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Middleware to keep the connection secure
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. This serves your "Face" (index.html)
@app.get("/")
async def read_index():
    return FileResponse('index.html')

# 2. This is the "Engine" (where your backend logic runs)
class RequestData(BaseModel):
    text: str

@app.post("/explain")
def explain_text(data: RequestData):
    # This acts as the bridge to your brain.py logic
    return {"result": f"Heuristic Engine analysis for: {data.text}"}