const messages = document.getElementById("messages");
const input = document.getElementById("userText");
const sendBtn = document.getElementById("sendBtn");

function addMessage(text, cls="user") {
  const d = document.createElement("div");
  d.className = cls;
  d.innerText = text;
  messages.appendChild(d);
  messages.scrollTop = messages.scrollHeight;
}

sendBtn.onclick = async () => {
  const text = input.value.trim();
  if(!text) return;
  addMessage("You: " + text, "user");
  input.value = "";
  // send to FastAPI
  const payload = {
    customer_id: "cust_1",
    text: text,
    lat: 18.5204,
    lon: 73.8567
  };
  addMessage("Thinking...", "bot-thinking");
  const res = await fetch("http://localhost:8001/api/message", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(payload)
  });
  const data = await res.json();
  // remove thinking
  const thinking = document.querySelector(".bot-thinking");
  if(thinking) thinking.remove();
  // display assistant
  const assistantText = data.assistant_raw || "No response";
  addMessage("Bot: " + assistantText, "bot");
  // optional: show context card for judges
  const cc = JSON.stringify(data.context_card, null, 2);
  addMessage("Context: " + cc, "context");
};
