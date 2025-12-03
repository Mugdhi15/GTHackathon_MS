console.log("ChatJS Loaded v6 — Guaranteed GPS Fix");

const messages = document.getElementById("messages");
const input = document.getElementById("userText");
const sendBtn = document.getElementById("sendBtn");

/* -------------------------------------------------------------------
   ALWAYS FETCH LOCATION *BEFORE* sending → avoids null lat/lon problem
--------------------------------------------------------------------*/
function getLiveLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) {
      console.warn("No geolocation API — using fallback Pune coords");
      return resolve({ lat: 18.5204, lon: 73.8567 });
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        resolve({
          lat: pos.coords.latitude,
          lon: pos.coords.longitude
        });
      },
      (err) => {
        console.warn("GPS blocked — fallback used", err);
        resolve({ lat: 18.5204, lon: 73.8567 }); 
      }
    );
  });
}

/* ------------------------------- */
function addMessage(text, cls = "user") {
  const d = document.createElement("div");
  d.className = cls;
  d.innerText = text;
  messages.appendChild(d);
  messages.scrollTop = messages.scrollHeight;
}

/* ------------------------------- */
function renderContextCard(ctx) {
  const card = document.createElement("div");
  card.className = "context-card";

  const weatherText = `${ctx.weather.condition || "Unknown"} (${ctx.weather.temperature || "?"})`;
  const locationText = `${ctx.store.name || "Unknown"} (${ctx.store.distance || "?"})`;
  const offerText = ctx.offers?.length ? ctx.offers[0].offer : "No active offers";

  card.innerHTML = `
    <h3>Context Card</h3>

    <div class="cc-row">
      <span class="cc-icon">☀️</span>
      <div>
        <div class="cc-title">Weather</div>
        <div class="cc-value">${weatherText}</div>
      </div>
    </div>

    <div class="cc-row">
      <span class="cc-icon">📍</span>
      <div>
        <div class="cc-title">Location</div>
        <div class="cc-value">${locationText}</div>
      </div>
    </div>

    <div class="cc-row">
      <span class="cc-icon">🏷</span>
      <div>
        <div class="cc-title">Offers</div>
        <div class="cc-value">${offerText}</div>
      </div>
    </div>
  `;

  messages.appendChild(card);
  messages.scrollTop = messages.scrollHeight;
}

/* ------------------------------------------------------------------- */
sendBtn.onclick = async () => {
  const text = input.value.trim();
  if (!text) return;

  addMessage("You: " + text, "user");
  input.value = "";

  addMessage("Thinking...", "bot-thinking");

  // ⭐ WAIT for GPS here — fixes your location not updating
  const gps = await getLiveLocation();
  console.log("Fetched GPS:", gps);

  const payload = {
    customer_id: "cust_1",
    text,
    lat: gps.lat,
    lon: gps.lon
  };

  let res;
  try {
    res = await fetch("http://localhost:8001/api/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } catch (err) {
    addMessage("Bot: (Network error)", "bot");
    console.error("Network error:", err);
    return;
  }

  // remove "Thinking..."
  const thinking = document.querySelector(".bot-thinking");
  if (thinking) thinking.remove();

  let data;
  try {
    data = await res.json();
  } catch (err) {
    addMessage("Bot: (Invalid JSON from backend)", "bot");
    console.error("JSON parse error:", err);
    return;
  }

  // final bot reply
  addMessage("Bot: " + (data.reply || "No response"), "bot");

  // show context card
  if (data.context_card) {
    renderContextCard(data.context_card);
  }
};
