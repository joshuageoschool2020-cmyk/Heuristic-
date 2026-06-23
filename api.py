from fastapi import FastAPI, Response
from pydantic import BaseModel
import uvicorn
from brain import process_concept

app = FastAPI()

# --- CSS and HTML combined for maximum reliability ---
PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background-color: #0A0A0A; color: white; font-family: sans-serif; text-align: center; padding: 50px; }
        .btn { background-color: #2563eb; color: white; padding: 15px 30px; border-radius: 25px; text-decoration: none; font-weight: bold; }
        .box { border: 1px solid #333; padding: 20px; border-radius: 10px; max-width: 500px; margin: auto; }
        textarea { width: 100%; height: 100px; background: black; color: white; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div id="content">
        <h1>DEPLOY ADVANCED COGNITIVE ANALYTICS.</h1>
        <a href="/app" class="btn">LAUNCH ENGINE</a>
    </div>
    <script>
        if (window.location.pathname === '/app') {
            document.getElementById('content').innerHTML = `
                <div class="box">
                    <h1>HEURISTIC_ENGINE</h1>
                    <textarea id="in"></textarea>
                    <button onclick="run()">Run Analysis</button>
                    <div id="out" style="margin-top:20px;">Result...</div>
                </div>
            `;
        }
        async function run() {
            const text = document.getElementById('in').value;
            const res = await fetch('/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            });
            const data = await res.json();
            document.getElementById('out').innerText = data.result;
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def read_root():
    return Response(content=PAGE_HTML, media_type="text/html")

@app.get("/app")
async def read_app():
    return Response(content=PAGE_HTML, media_type="text/html")

class RequestData(BaseModel):
    text: str

@app.post("/explain")
def explain_text(data: RequestData):
    return {"result": process_concept(data.text)}

if __name__ == "__main__":
    import os
    uvicorn.run("api:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))