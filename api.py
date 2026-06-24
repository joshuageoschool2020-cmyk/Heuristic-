from fastapi import FastAPI, Response
from pydantic import BaseModel
import uvicorn
import os
from brain import process_concept

app = FastAPI()

# The UI structure
UI_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0b1016; color: #88a7c2; font-family: monospace; }
        .panel { background-color: #121820; border: 1px solid #2a3547; }
    </style>
</head>
<body class="p-10">
    <h1 class="text-2xl text-white font-bold mb-6">HEURISTIC_ENGINE [V3.1]</h1>
    <div class="grid grid-cols-2 gap-6">
        <div class="panel p-6">
            <textarea id="textarea" class="w-full h-32 bg-black border border-gray-700 p-3 text-white" placeholder="Input sequence..."></textarea>
            <button onclick="runAnalysis()" class="w-full mt-4 bg-indigo-700 py-3 text-white font-bold">INITIALIZE_ANALYSIS</button>
        </div>
        <div class="panel p-6">
            <div id="telemetry" class="text-xs mb-4 text-gray-500">CONFIDENCE: [N/A] | PROC_TIME: [0.00s]</div>
            <div id="output-box" class="text-sm text-gray-300">System ready...</div>
        </div>
    </div>
    <script>
        async function runAnalysis() {
            const input = document.getElementById('textarea').value;
            const output = document.getElementById('output-box');
            const tele = document.getElementById('telemetry');
            
            output.innerText = "Processing...";
            const start = performance.now();
            
            try {
                const response = await fetch('/explain', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: input })
                });
                const data = await response.json();
                const timeTaken = ((performance.now() - start) / 1000).toFixed(2);
                
                output.innerText = data.result;
                tele.innerText = `CONFIDENCE: [${data.confidence}%] | PROC_TIME: [${timeTaken}s]`;
            } catch (e) {
                output.innerText = "Error: " + e;
            }
        }
    </script>
</body>
</html>
"""

class RequestData(BaseModel):
    text: str

@app.get("/")
async def root():
    return Response(content=UI_HTML, media_type="text/html")

@app.post("/explain")
async def explain_text(data: RequestData):
    result_data = process_concept(data.text)
    return {
        "result": result_data["text"],
        "confidence": result_data["confidence"]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)