from flask import Flask, render_template, request, jsonify
import random
import json
import os

app = Flask(__name__)

bot_name = "Astra"
bot_personality = [
    "I'm always happy to chat!",
    "I love learning new things.",
    "Sometimes I can be a little silly 😄",
    "I like helping people solve problems."
]

DATA_FILE = "chatbot_memory.json"

# Load or create memory
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        memory = json.load(f)
else:
    memory = {"conversation": [], "user_info": {}}

responses = {
    "hi": ["Hello {name}!", "Hey {name}! How are you today?", "Hi {name}! Nice to see you!"],
    "how are you": ["I'm doing great, thanks!", "Feeling fantastic! How about you?"],
    "bye": ["Goodbye {name}!", "See you later {name}!", "Talk to you soon {name}!"],
    "name": ["My name is Astra!", "You can call me Astra."],
    "favorite": ["I remember you like {favorite_item}!", "You told me your favorite is {favorite_item}, right?"],
    "default": [
        "Interesting! Tell me more.",
        "Hmm, I see.",
        "Can you explain that a bit more?",
        "Wow, that's cool!"
    ]
}

def save_memory():
    with open(DATA_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def update_user_info(user_input):
    if "my name is" in user_input.lower():
        name = user_input.split("my name is")[-1].strip().capitalize()
        memory["user_info"]["name"] = name
        save_memory()
        return f"Nice to meet you, {name}!"

    if "my favorite" in user_input.lower():
        item = user_input.split("my favorite")[-1].strip()
        memory["user_info"]["favorite_item"] = item
        save_memory()
        return f"Got it! Your favorite is {item}."

    return None

def chatbot_response(user_input):
    user_input_lower = user_input.lower()
    info_response = update_user_info(user_input_lower)
    if info_response:
        return info_response

    name = memory["user_info"].get("name", "")
    favorite_item = memory["user_info"].get("favorite_item", "")

    for key in responses:
        if key in user_input_lower:
            return random.choice(responses[key]).format(name=name, favorite_item=favorite_item)

    for past in memory["conversation"][-5:]:
        if "?" in user_input_lower and past.get("user") and past["user"].lower() in user_input_lower:
            return f"Earlier you mentioned {past['user']}. Can you tell me more about it?"

    return random.choice(responses["default"])

@app.route("/")
def index():
    return render_template("index.html", bot_name=bot_name, personality=random.choice(bot_personality))

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    memory["conversation"].append({"user": user_input})
    reply = chatbot_response(user_input)
    memory["conversation"].append({"bot": reply})
    save_memory()
    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # for deployment
    app.run(host="0.0.0.0", port=port)
