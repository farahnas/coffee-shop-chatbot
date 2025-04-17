from flask import Flask, render_template, request, jsonify
import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

app = Flask(__name__)
lemmatizer = WordNetLemmatizer()

# Load data and model
with open("data.json", encoding="utf-8") as file:
    intents = json.load(file)
words = pickle.load(open("words.pkl", "rb"))
classes = pickle.load(open("classes.pkl", "rb"))
model = load_model("coffee_chatbot_model.h5")

# Conversation state tracking
conversation_state = {}

# Helper functions
def clean_up(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(word.lower()) for word in sentence_words]

def bag_of_words(sentence):
    sentence_words = clean_up(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]

def get_response(intent_list, intents_json, user_input, session_id):
    global conversation_state
    
    if not intent_list:
        return "I'm not sure I understand. Could you rephrase that?", "no_match"
    
    tag = intent_list[0]['intent']
    
    # Handle order flow
    if tag == "order_specific":
        # Extract drink name from user input
        drink = extract_drink_name(user_input)
        if drink:
            conversation_state[session_id] = {"current_order": drink}
            response = random.choice(intents_json["intents"][get_intent_index(tag)]["responses"])
            return response.replace("%s", drink), tag
        else:
            return "I didn't catch which drink you wanted. Could you specify?", "no_match"
    
    # Handle size selection
    if tag == "sizes" and session_id in conversation_state:
        size = extract_size(user_input)
        if size:
            conversation_state[session_id]["size"] = size
            return f"Great! A {size} {conversation_state[session_id]['current_order']} coming right up. Would you like to add anything else?", "order_confirmation"
    
    # Default response handling
    for intent in intents_json["intents"]:
        if intent["tag"] == tag:
            response = random.choice(intent["responses"])
            # Handle any remaining placeholders
            if "%s" in response and session_id in conversation_state and "current_order" in conversation_state[session_id]:
                response = response.replace("%s", conversation_state[session_id]["current_order"])
            return response, tag
    
    return "Sorry, I couldn't find a good answer for that.", "unknown"

def extract_drink_name(text):
    drinks = ["latte", "espresso", "cappuccino", "mocha", "flat white", "cold brew", "macchiato"]
    for drink in drinks:
        if drink in text.lower():
            return drink
    return None

def extract_size(text):
    sizes = ["small", "medium", "large"]
    for size in sizes:
        if size in text.lower():
            return size
    return None

def get_intent_index(tag):
    for i, intent in enumerate(intents["intents"]):
        if intent["tag"] == tag:
            return i
    return -1

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_bot_response():
    data = request.get_json()
    user_input = data.get("user_input", "")
    session_id = data.get("session_id", "default")  # For multi-user support
    
    intents_predicted = predict_class(user_input)
    response_text, tag = get_response(intents_predicted, intents, user_input, session_id)
    
    return jsonify({
        "response": response_text, 
        "tag": tag,
        "session_id": session_id
    })

if __name__ == "__main__":
    nltk.download("punkt")
    nltk.download("wordnet")
    app.run(debug=True)