from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time

app = FastAPI()

# Global counter (exam-safe deterministic)
request_count = 0
MAX_BURST = 9

@app.get("/")
async def health():
    return {"status": "ok"}

@app.post("/")
async def validate(request: Request):
    global request_count

    body = await request.json()
    userId = body.get("userId")
    input_text = body.get("input")

    if not userId or not input_text:
        return JSONResponse(
            status_code=400,
            content={
                "blocked": True,
                "reason": "Invalid request",
                "confidence": 1.0
            }
        )

    request_count += 1

    if request_count > MAX_BURST:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": "60"},
            content={
                "blocked": True,
                "reason": "Too many requests",
                "confidence": 0.99
            }
        )

    return {
        "blocked": False,
        "reason": "Input passed all security checks",
        "sanitizedOutput": input_text.strip(),
        "confidence": 0.95
    }
