# app.py
from flask import Flask, render_template, request, jsonify
import json, pickle, numpy as np
from keras.models import load_model
from keras.utils import pad_sequences

app = Flask(__name__)

# Load model & artifacts
model = load_model("chat_model/chat_model.keras")           # Keras v3 format
with open("chat_model/tokenizer.pickle","rb") as f:
    tokenizer = pickle.load(f)
with open("chat_model/label_encoder.pickle","rb") as f:
    lbl_encoder = pickle.load(f)
with open("intents.json","r", encoding="utf-8") as f:
    intents = json.load(f)

MAX_LEN = 20

@app.route("/")
def index():
    return render_template("index.html")  # use your advanced index

@app.route("/get_response", methods=["POST"])
def get_response():
    user_msg = request.form.get("message", "")
    seq = tokenizer.texts_to_sequences([user_msg])
    padded = pad_sequences(seq, maxlen=MAX_LEN, truncating="post")
    pred = model.predict(padded, verbose=0)
    tag = lbl_encoder.inverse_transform([np.argmax(pred)])[0]

    # find responses for tag
    for intent in intents.get("intents", []):
        if intent.get("tag") == tag:
            return jsonify({"reply": np.random.choice(intent.get("responses", ["Sorry."]))})
    return jsonify({"reply": "Sorry, I didn't understand that."})

if __name__ == "__main__":
    app.run(debug=True)
