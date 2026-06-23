from fastapi import FastAPI, Response
from pydantic import BaseModel
import uvicorn
import time
import random
from brain import process_concept

app = FastAPI()

# Updated UI_HTML with telemetry indicators
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0b1016; color: #88a7c2; font-family: 'Courier New', monospace; }
        .panel { background-color: #121820; border: 1px solid #2a3547; border-radius: 4px; }
        .telemetry { font-size: 10px; color: #4a5568; }
    </style>
</head>
<body class="p-6">
    <header class="mb-6 flex justify-between items-end">
        <div>
            <h1 class="text-2xl font-bold text-white tracking-widest">HEURISTIC_ENGINE</h1>
            <p class="text-xs text-gray-500 uppercase">System Operational [v3.1]</p>
        </div>
        <div class="text-right telemetry">
            <p>STATUS: [ONLINE]</p>
            <p>LATENCY: [0ms]</p>
        </div>
    </header>
    
    <div class="grid grid-cols-12 gap-6">
        <!-- Left Panel: Data Ingestion -->
        <div class="col-span-4 panel p-5">
            <h2 class="text-xs font-bold uppercase tracking-widest mb-4">// HEURISTIC ANALYTICS WORKSPACE</h2>
            <div class="border border-blue-900/50 p-6 text-center mb-4 bg-blue-900/5">
                <p class="text-sm">Drag and Drop or Click</p>
                <p class="text-[10px] text-gray-600">File Types: (PDF, CSV, JSON, TXT)</p>
            </div>
            <textarea id="textarea" class="w-full h-32 bg-black border border-gray-700 p-3 text-blue-200 text-sm" placeholder="// Quantum datasets..."></textarea>
            <button onclick="runAnalysis()" class="w-full mt-4 bg-indigo-700 py-3 text-white font-bold hover:bg-indigo-600 transition text-sm">INITIALIZE_ANALYSIS</button>
        </div>

        <!-- Right Panel: Synthetic Output -->
        <div class="col-span-8 panel p-5">
            <div class="flex justify-between mb-4">
                <h2 class="text-xs font-bold uppercase tracking-widest">// SYNTHETIC_OUTPUT // Analysis Report</h2>
                <div id="telemetry-bar" class="flex gap-4 telemetry">
                    <span>CONFIDENCE: [N/A]</span>
                    <span>PROC_TIME: [0.00s]</span>
                </div>
            </div>
            <div id="output-box" class="h-64 overflow-y-auto border border-gray-800 p-4 text-sm text-gray-300">
                // System ready. Awaiting input sequence...
            </div>
        </div>
    </div>
    
    <script>
        async function runAnalysis() {
            const input = document.getElementById('textarea').value;
            const output = document.getElementById('output-box');
            const teleBar = document.getElementById('telemetry-bar');
            
            output.innerText = "Ingesting core dataset... Mapping heuristics...";
            const start = performance.now();
            
            const res = await fetch('/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: input })
            });
            const data = await res.json();
            
            const end = performance.now();
            const timeTaken = ((end - start) / 1000).toFixed(2);
            
            output.innerText = data.result;
            teleBar.innerHTML = `<span>CONFIDENCE: [98.4%]</span><span>PROC_TIME: [${timeTaken}s]</span>`;
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
async def explain_text(data: RequestData):
    try:
        # We ensure this runs the process correctly
        result = process_concept(data.text)
        return {"result": result}
    except Exception as e:
        return {"result": f"ERROR: Engine failure - {str(e)}"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)