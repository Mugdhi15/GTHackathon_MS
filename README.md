🚀 H-002 | Customer Experience Automation
Track: Customer Experience & Conversational AI
=============================================

> **ContextOS** — The Hyper-Personalized Customer Experience Engine
“Turning vague customer messages into real-world actions in under 2 seconds.”

1\. The Problem (Real World Scenario)
-------------------------------------

**Context:** Retail customers today expect instant, context-aware answers:

- “Is this store open?”

- “Do you have Hot Cocoa?”

- “I’m cold, where can I go?”

But standard chatbots fail — they respond generically, don’t understand user context, and can’t use store data, customer history, or location.

<!-- **The Pain Point:** This manual process is slow, boring, and error-prone. If a campaign is wasting budget, the client might not know for days because the reporting lag is too high. -->

> **My Solution:** I built **ContextOS**, a real-time AI system that merges customer location, store data, preferences, and RAG-retrieved documents to produce actionable, hyper-personalized responses — instantly.

2\. Expected End Result
-----------------------

**For the User:**

*   **Input:** Type a natural message into the chat (e.g., “I’m cold”).
    
*   **Action:** The system automatically fetches location, weather, offers, and store data.
    
*   **Output:** A precise, real-world recommendation like:

> **Sample response:** “There’s a Starbucks 43m away. Hot Cocoa is in stock, and you have a 10% loyalty discount. It’s currently 17°C outside — come inside and warm up!”

The system intelligently merges:

- RAG-retrieved inventory/policy documents
- Customer history & loyalty
- Use live weather + location  
- Emotion analysis    
- Understand vague inputs     

3\. Technical Approach
----------------------

ContextOS is built as a production-minded architecture, with clear separation between Frontend (Django), Backend (FastAPI), RAG (ChromaDB), and **LLM intelligence (OpenAI)**.

**System Architecture:**

## **System Architecture**

1. **Frontend (Django Web UI):**  
   A clean HTML/CSS/JS chat interface hosted on Django. It captures user messages and sends them to the backend API in real-time.

2. **Backend (FastAPI Microservice):**  
   All intelligence runs inside a dedicated FastAPI service, responsible for:
   - Message processing  
   - Session context management  
   - PII masking  
   - Integrations (Weather, Places API)  
   - RAG vector search  
   - LLM generation  

3. **PII Masking Layer (`masking.py`):**  
   Before any text reaches an LLM:
   - Phone numbers → `[PHONE]`  
   - Names → `[NAME]`  
   - Order IDs → `[ORDER_ID]`  
   Local regex-based masking ensures **no sensitive data leaves the system**.

4. **Context Builder (The Brain):**
   This orchestrator combines multiple real-time signals:
   - User text  
   - Google Places store proximity  
   - OpenWeather temperature & conditions  
   - Customer profile & preferences  
   - In-session history  
   - Inventory & offers JSON  
   - RAG search results from PDFs  
   
   It outputs a structured **Context Card**, which guarantees grounded reasoning.

5. **RAG Engine (ChromaDB + Sentence Transformers):**  
   PDFs, policies, and store inventory docs are embedded and stored in a vector DB.  
   A similarity search returns the **top chunks relevant to the user query**.

6. **External Signals (Live APIs):**
   - **Google Places API:** Finds the nearest store, café, or outlet based on latitude/longitude.  
   - **OpenWeather API:** Helps the bot give temperature-aware suggestions (e.g., “It’s 17°C near you”).  

7. **Generative AI (The Assistant):**
   - Uses **OpenAI GPT-4o-mini** or **Local LM Studio** model via API.  
   - Response generation follows a **Strict-Context Prompt** containing only:  
     - Masked user text  
     - Context card  
     - Verified store/weather/inventory data  
   - This prevents hallucinations and ensures the output is grounded.

8. **Session Manager:**
   A lightweight in-memory store that preserves:  
   - Past messages  
   - Recent offers surfaced  
   - Previous store suggestions  
   - User’s last intent  
   
   This creates a **multi-turn conversational memory** without using cookies or frontend storage.

9. **Response Formatter:**
   Produces the final output in a structured JSON:
   ```json
   {
     "reply": "...",
     "action": "navigate | redeem_offer | give_info",
     "context_card": { ... }
   }


4\. Tech Stack
--------------

| Category | Tools |
|----------|-------|
| **Frontend** | Django, HTML, CSS, JS |
| **Backend** | FastAPI (Python 3.11) |
| **RAG** | ChromaDB + SentenceTransformers |
| **LLM** | OpenAI GPT-4o-mini / Local LM Studio |
| **Data APIs** | Google Places, OpenWeather |
| **Security** | Regex PII Masking |
| **Storage** | JSON + Vector DB |
| **Other** | dotenv, requests |
    

5\. Challenges & Learnings
--------------------------
_ Major hurdles I overcame are:_

---

### **Challenge 1: Preventing LLM Hallucinations**

- **Issue:**  
  Early versions of the assistant made up store details, inventory values, and reasons for suggestions (e.g., “This store is open 24/7” even when not provided in data).

- **Solution:**  
  I implemented a **Strict-Context Prompting Framework**.  
  The LLM was instructed:  
  *“Only use data present in the Context Card (RAG + JSON). If information is missing, respond with ‘Unknown’.”*  
  This drastically reduced hallucinations and kept responses grounded in real data.

---

### **Challenge 2: Safe Handling of Sensitive Data (PII)**

- **Issue:**  
  The raw user text often included phone numbers, names, or order references that **cannot be sent to public LLM APIs**.

- **Solution:**  
  I built a dedicated **PII Masking Layer (`masking.py`)** using regex rules:  
  - Phone numbers → `[PHONE]`  
  - Names → `[NAME]`  
  - Order IDs → `[ORDER_ID]`  
  This ensured full compliance and safe data processing without relying on external libraries.

---

### **Challenge 3: Real-Time Context Fusion**

- **Issue:**  
  Combining weather, location, customer preferences, RAG documents, and current inventory into one unified reasoning layer created conflicting signals.

- **Solution:**  
  I built a **Context Builder Orchestrator** that normalizes all signals into a structured “Context Card.”  
  This allowed the LLM to reason cleanly and consistently based on a single, well-defined input object.

---

### **Challenge 4: Store Proximity & API Rate Limits**

- **Issue:**  
  The Google Places API frequently throttled search queries during rapid testing.

- **Solution:**  
  Implemented **radius-based caching**.  
  If the user stayed within the same 100m geo-cell, the system re-used cached store results instead of calling the API repeatedly.

---

### **Challenge 5: Managing Session Memory**

- **Issue:**  
  The assistant forgot earlier user context (e.g., last store mentioned, previous offers surfaced), reducing personalization.

- **Solution:**  
  Added an **in-memory session store** that maintains conversation history, last intent, last known location, recent recommendations, and preference patterns.

---

## **Learnings**
- Designing for **real-world context** requires fusing multiple noisy signals smoothly.  
- A grounded LLM works best when fed a **strict, validated context card** instead of raw text.  
- Privacy-first design (masking before inference) is essential for production use.  
- Multi-turn conversational intelligence depends heavily on **session architecture**, not just model intelligence.

    

6\. Visual Proof
----------------

**Anomaly Detected (Terminal)**

**Final Report (PDF)**

_Terminal showing Isolation Forest detecting outliers_

_Final Output sent to client via Email_

7\. How to Run
--------------

```bash
# 1. Clone
git clone https://github.com/Mugdhi15/GTHackathon_MS
cd GTHackathon_MS

# 2. Setup Environment
cp .env.example .env
# Add:
# OPENAI_API_KEY=
# GOOGLE_PLACES_API=
# OPENWEATHER_API=
# CHROMA_PERSIST_DIR=./chroma_db

# 3. Install
pip install -r requirements.txt

# 4. Build RAG DB
cd ingest
python ingest_to_chroma.py

# 5. Start FastAPI
cd fastapi_service
uvicorn main:app --reload --port 8001

# 6. Start Django
cd django_frontend
python manage.py runserver 8000

# 7. Open
http://localhost:8000
```