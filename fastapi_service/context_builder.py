# context_builder.py
import json, os, asyncio
from .masking import mask_pii
from .rag_client import query_rag
import openai
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# load local JSONs
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
with open(os.path.join(BASE_DIR,"data/customers.json")) as f:
    CUSTOMERS = json.load(f)
with open(os.path.join(BASE_DIR,"data/offers.json")) as f:
    OFFERS = json.load(f)
with open(os.path.join(BASE_DIR,"data/inventory.json")) as f:
    INVENTORY = json.load(f)

def simple_emotion_detect(text):
    txt = text.lower()
    if any(w in txt for w in ["cold","freezing","chilly","freeze"]):
        return "cold"
    if any(w in txt for w in ["angry","frustrated","upset","mad","not happy"]):
        return "frustrated"
    if any(w in txt for w in ["lost","where","directions","how to get"]):
        return "lost"
    return "neutral"

async def build_context_and_response(customer_id, text, lat=None, lon=None):
    # 1. Mask text
    masked = mask_pii(text)

    # 2. Build base context
    customer = CUSTOMERS.get(customer_id, {})
    emotion = simple_emotion_detect(text)

    # 3. RAG lookup
    rag_results = query_rag(text, top_k=3)

    # 4. Inventory/Offer matching (very simple)
    # Suppose lat/lon maps to a store — for demo, pick Starbucks_MG_Road
    nearby_store = "Starbucks_MG_Road"
    inv = INVENTORY.get(nearby_store, {})
    offer_matches = [o for o in OFFERS if "Hot Cocoa" in o.get("offer","") or "Hot Cocoa" in " ".join(o.get("tags",[]))]

    context_card = {
        "masked_user_text": masked,
        "emotion": emotion,
        "nearby_store": nearby_store,
        "inventory_match": inv,
        "offers": offer_matches,
        "rag_snippets": rag_results,
        "customer": {"id":customer_id, **customer}
    }

    # 5. Compose final prompt for OpenAI (masking ensured)
    prompt = f"""
You are a helpful customer assistant. Use the context below to generate a short, actionable reply (<= 80 words).
Do NOT output any raw PII (masking already applied).

CONTEXT:
User text: {masked}
Emotion: {emotion}
Customer history: {customer.get('past_purchases',[])}
Nearby store inventory: {inv}
Offers: {offer_matches}
RAG extracts: {[(r['text'][:200], r['meta']) for r in rag_results]}

Provide:
1) "reply": a short message to the user
2) "action": (one of "navigate","redeem_offer","give_info","ask_followup")
3) "explain": 1-line explanation of why the suggestion was chosen
"""
    # call OpenAI (or LM Studio if you have local model)
    resp = openai.ChatCompletion.create(model="gpt-4o-mini", # you can replace with gpt-4o or gpt-4 if available
                                        messages=[{"role":"user","content":prompt}],
                                        max_tokens=200, temperature=0.2)
    gtext = resp['choices'][0]['message']['content'].strip()
    # For reliability, return both generated text and context card
    return {"context_card":context_card, "assistant_raw": gtext}
