import os
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

# Groq API Client setup (Render ke Environment Variable se key uthayega)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Frontend HTML / UI (Ekdum clean aur responsive chat screen)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Private AI App</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; display: flex; flex-direction: column; height: 90vh; }
        h2 { text-align: center; color: #38bdf8; }
        #chat-box { flex: 1; border: 1px solid #334155; border-radius: 8px; padding: 15px; overflow-y: auto; background: #1e293b; margin-bottom: 15px; }
        .message { margin-bottom: 12px; padding: 10px 14px; border-radius: 6px; line-height: 1.4; max-width: 80%; }
        .user { background: #0284c7; margin-left: auto; text-align: right; }
        .ai { background: #334155; margin-right: auto; }
        .input-area { display: flex; gap: 10px; }
        input { flex: 1; padding: 12px; border-radius: 6px; border: 1px solid #475569; background: #0f172a; color: white; font-size: 16px; }
        button { padding: 12px 20px; background: #0284c7; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; }
        button:hover { background: #0ea5e9; }
    </style>
</head>
<body>
    <h2>🔒 My Private AI App</h2>
    <div id="chat-box">
        <div class="message ai">Hello! Main aapka private AI assistant hoon. Bataiye aaj main aapki kya madad karoon?</div>
    </div>
    <div class="input-area">
        <input type="text" id="user-input" placeholder="Yahan apna sawal likhiye..." onkeydown="if(event.key === 'Enter') sendMessage()">
        <button onclick="sendMessage()">Bhejo</button>
    </div>

    <script>
        async function sendMessage() {
            const inputField = document.getElementById('user-input');
            const chatBox = document.getElementById('chat-box');
            const text = inputField.value.trim();
            if(!text) return;

            chatBox.innerHTML += `<div class="message user">${text}</div>`;
            inputField.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                chatBox.innerHTML += `<div class="message ai">${data.reply || data.error}</div>`;
            } catch (err) {
                chatBox.innerHTML += `<div class="message ai" style="color: #f87171;">Network error, kripya dobara try karein.</div>`;
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not client.api_key:
            return jsonify({"error": "Groq API Key missing! Kripya Render par Environment Variable check karein."}), 500

        # Groq API ko call karna (Super-fast Llama model)
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful, concise private AI assistant."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        
        ai_reply = completion.choices[0].message.content
        return jsonify({"reply": ai_reply})

    except Exception as e:
        return jsonify({"error": f"Error aaya: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
