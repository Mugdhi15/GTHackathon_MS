import os
import json
from dotenv import load_dotenv

from fastapi_service.masking import mask_pii
from fastapi_service.rag_client import query_rag
from fastapi_service.utils import get_weather, get_nearby_store, get_nearby_places_osm

from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load data
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CUSTOMERS = json.load(open(os.path.join(BASE, "data/customers.json")))
OFFERS = json.load(open(os.path.join(BASE, "data/offers.json")))
INVENTORY = json.load(open(os.path.join(BASE, "data/inventory.json")))

SESSION = {}

def simple_emotion_detect(text):
    t = text.lower()
    if any(w in t for w in ["cold", "freezing"]): return "cold"
    if any(w in t for w in ["angry", "frustrated"]): return "frustrated"
    return "neutral"


async def build_context_and_response(customer_id, text, lat, lon):

    masked_text = mask_pii(text)
    weather = get_weather(lat, lon)

    # ⭐ FIRST TRY REAL OPENSTREETMAP SHOPS
    places = get_nearby_places_osm(lat, lon, query="cafe")

    if places:
        store = {
            "name": places[0]["name"],
            "distance": "Nearby"
        }
    else:
        store = get_nearby_store(lat, lon)  # fallback

    # Static inventory (for now)
    inventory = INVENTORY.get("Starbucks_MG_Road", {})

    rag_results = query_rag(text)
    emotion = simple_emotion_detect(text)
    offers = [o for o in OFFERS if "Hot" in o["offer"]]

    if customer_id not in SESSION:
        SESSION[customer_id] = {"history": []}

    SESSION[customer_id]["history"].append(masked_text)

    context_card = {
        "emotion": emotion,
        "weather": weather,
        "store": store,
        "inventory": inventory,
        "offers": offers,
        "rag_snippets": rag_results,
        "history": SESSION[customer_id]["history"][-5:],
        "customer": CUSTOMERS.get(customer_id, {})
    }

    prompt = f"""
You are ContextOS, a grounded AI assistant.
ONLY use the structured data below.
If any info is missing, say "Unknown".

Context:
{json.dumps(context_card, indent=2)}

User said: "{masked_text}"

Respond with:
1. reply (1–2 sentences only)
2. action (navigate | redeem_offer | give_info)
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=150
    )

    reply_raw = completion.choices[0].message.content.strip()
    print("LLM RAW REPLY:", reply_raw)

    # Clean format
    lines = reply_raw.split("\n")
    clean_reply = lines[0].replace("1.", "").strip()
    action = (lines[1].replace("2.", "").strip() if len(lines) > 1 else "unknown")

    return {
        "reply": clean_reply,
        "action": action,
        "context_card": context_card
    }
