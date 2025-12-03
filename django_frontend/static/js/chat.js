console.log("ChatJS Loaded v4");

const messages = document.getElementById("messages");
const input = document.getElementById("userText");
const sendBtn = document.getElementById("sendBtn");

/* -------------------------------
   Helper: Add a chat bubble
--------------------------------*/
function addMessage(text, cls = "user") {
  const d = document.createElement("div");
  d.className = cls;
  d.innerText = text;
  messages.appendChild(d);
  messages.scrollTop = messages.scrollHeight;
}

/* -------------------------------
   Helper: Render Context Card
--------------------------------*/
function renderContextCard(ctx) {
  const card = document.createElement("div");
  card.className = "context-card";

  let weatherText = `${ctx.weather.condition || "Unknown"} (${ctx.weather.temperature || "?"}°)`;
  let locationText = `${ctx.store.name || "Unknown"} (${ctx.store.distance || "?"})`;
  let offerText = ctx.offers.length ? ctx.offers[0].offer : "No active offers";

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

/* -------------------------------
   Main Send Handler
--------------------------------*/
sendBtn.onclick = async () => {
  const text = input.value.trim();
  if (!text) return;

  addMessage("You: " + text, "user");
  input.value = "";

  addMessage("Thinking...", "bot-thinking");

  const payload = {
    customer_id: "cust_1",
    text: text,
    lat: 18.5204,
    lon: 73.8567
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

  // remove thinking bubble
  const thinking = document.querySelector(".bot-thinking");
  if (thinking) thinking.remove();

  // parse JSON
  let data;
  try {
    data = await res.json();
  } catch (err) {
    addMessage("Bot: (Invalid JSON response)", "bot");
    console.error("JSON parse error:", err);
    return;
  }

  // extract bot reply
  const assistantText = (data && data.reply)
    ? data.reply
    : "No response from AI";

  addMessage("Bot: " + assistantText, "bot");

  // render context card
  if (data && data.context_card) {
    renderContextCard(data.context_card);
  }
};
