from fastapi import FastAPI, Response
from pydantic import BaseModel
import uvicorn
from brain import process_concept

app = FastAPI()

# This is the updated UI_HTML without the user name
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0c121c; color: #78a1bb; font-family: 'Courier New', monospace; }
        .panel { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; }
    </style>
</head>
<body class="p-6">
    <header class="mb-6 border-b border-gray-700 pb-4">
        <h1 class="text-xl font-bold text-white">HEURISTIC_ENGINE</h1>
        <p class="text-xs text-gray-400">SYSTEM OPERATIONAL [v3.1]</p>
    </header>
    
    <div class="grid grid-cols-2 gap-6">
        <!-- Input Panel -->
        <div class="panel p-5">
            <h2 class="text-blue-300 mb-3 font-bold uppercase text-sm tracking-widest">// DATA INGESTION PANEL</h2>
            <div class="border-2 border-dashed border-gray-600 p-6 text-center mb-4">
                <p>Drag and Drop or Click</p>
            </div>
            <textarea id="textarea" class="w-full h-32 bg-black border border-gray-600 p-3 text-blue-200" placeholder="// Raw Concept Entry..."></textarea>
            <button onclick="runAnalysis()" class="w-full mt-4 bg-blue-700 py-2 font-bold hover:bg-blue-600">INITIALIZE_ANALYSIS</button>
        </div>

        <!-- Output Panel -->
        <div class="panel p-5">
            <h2 class="text-blue-300 mb-3 font-bold uppercase text-sm tracking-widest">// SYNTHETIC_OUTPUT // Analysis Report</h2>
            <div id="output-box" class="h-64 overflow-y-auto border border-gray-700 p-4 text-sm text-gray-300">
                // Awaiting input sequence...
            </div>
        </div>
    </div>
    
    <script>
        async function runAnalysis() {
            const input = document.getElementById('textarea').value;
            const output = document.getElementById('output-box');
            output.innerText = "Processing sequence...";
            const res = await fetch('/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: input })
            });
            const data = await res.json();
            output.innerText = data.result;
        }
    </script>
</body>
</html>
"""

@app.get("/")
@app.get("/app")
async def serve_ui():
    return Response(content=UI_HTML, media_type="text/html")

class RequestData(BaseModel):
    text: str

@app.post("/explain")
def explain_text(data: RequestData):
    return {"result": process_concept(data.text)}

if __name__ == "__main__":
    import os
    uvicorn.run("api:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))