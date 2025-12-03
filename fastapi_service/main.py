# main.py
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from .context_builder import build_context_and_response

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_DIR = os.getenv("CHROMA_PERSIST_DIR")

app = FastAPI()
origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])

@app.post("/api/message")
async def message(request: Request):
    payload = await request.json()
    # expected payload: { "customer_id":"cust_1", "text":"I'm cold", "lat":..., "lon":... }
    cust_id = payload.get("customer_id")
    text = payload.get("text", "")
    lat = payload.get("lat")
    lon = payload.get("lon")
    result = await build_context_and_response(customer_id=cust_id, text=text, lat=lat, lon=lon)
    return JSONResponse(result)
