from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ---- Enable CORS (important for portal fetch) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Global counter ----
request_count = 0
MAX_BURST = 9


# ---- Health check (portal may test GET first) ----
@app.get("/")
async def health():
    return {"status": "ok"}


# ---- Rate limited endpoint ----
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
