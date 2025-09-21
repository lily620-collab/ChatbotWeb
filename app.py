from flask import Flask, render_template, request, jsonify, session
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = "super_secret_key_123"  # Needed for sessions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(BASE_DIR, "chatbot_memory.json")

# Load or create memory safely
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({}, f)

try:
    with open(MEMORY_FILE, "r") as f:
        memory = json.load(f)
except json.JSONDecodeError:
    memory = {}
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f)

bot_name = "Astra"
personality = "Friendly AI chatbot that remembers you!"

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def get_user_id():
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
    return session["user_id"]

def get_user_memory(user_id):
    if user_id not in memory:
        memory[user_id] = {"conversation": [], "user_info": {}}
    return memory[user_id]

def update_user_info(user_memory, user_input):
    user_input_lower = user_input.lower()

    if "my name is" in user_input_lower:
        name = user_input.split("my name is")[-1].strip().capitalize()
        user_memory["user_info"]["name"] = name
        return f"Nice to meet you, {name}!"

    if "i am" in user_input_lower and "years old" in user_input_lower:
        age = ''.join([c for c in user_input_lower if c.isdigit()])
        if age:
            user_memory["user_info"]["age"] = age
            return f"Wow, {age} years old! Cool!"

    if "my hobby is" in user_input_lower:
        hobby = user_input.split("my hobby is")[-1].strip()
        user_memory["user_info"]["hobby"] = hobby
        return f"Nice! I will remember that your hobby is {hobby}."

    if "my favorite food is" in user_input_lower:
        food = user_input.split("my favorite food is")[-1].strip()
        user_memory["user_info"]["favorite_food"] = food
        return f"Yum! I will remember that your favorite food is {food}."

    if "my favorite" in user_input_lower:
        item = user_input.split("my favorite")[-1].strip()
        user_memory["user_info"]["favorite_item"] = item
        return f"Got it! Your favorite is {item}."

    return None

@app.route("/")
def home():
    return render_template("index.html", bot_name=bot_name, personality=personality)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.get_json().get("message", "")
    user_id = get_user_id()
    user_memory = get_user_memory(user_id)

    response = update_user_info(user_memory, user_input)
    if not response:
        response = f"I heard you say: {user_input}"

    user_memory["conversation"].append({"user": user_input, "bot": response})
    memory[user_id] = user_memory
    save_memory()

    return jsonify({"reply": response})

# Render-friendly host & port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


