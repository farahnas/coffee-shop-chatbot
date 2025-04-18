import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import load_model

lemmatizer = WordNetLemmatizer()

with open("data.json", encoding="utf-8") as file:
    intents = json.load(file)
words = pickle.load(open("words.pkl", "rb"))
classes = pickle.load(open("classes.pkl", "rb"))
model = load_model("coffee_chatbot_model.h5")

def clean_up(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

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

def get_response(intent_list, intents_json):
    tag = intent_list[0]["intent"]
    for i in intents_json["intents"]:
        if i["tag"] == tag:
            return random.choice(i["responses"])

print("CoffeeBot ☕ is ready to chat! (type 'quit' to exit)")
while True:
    message = input("You: ")
    if message.lower() == "quit":
        break
    ints = predict_class(message)
    res = get_response(ints, intents)
    print("CoffeeBot:", res)
