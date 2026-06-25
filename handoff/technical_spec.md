# Architecture Specifications
- Frontend: HTML/JS using fetch API to communicate with backend.
- Backend: FastAPI (api.py).
- Core Logic: brain.py (process_concept function).
- Data Contract: Frontend sends text input; Backend returns JSON: {"text": str, "confidence": float}.
- Deployment: Render (Web Service).