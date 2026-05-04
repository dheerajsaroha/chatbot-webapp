# app.py - OPTIMIZED VERSION
from flask import Flask, render_template, request, jsonify
import json, pickle, numpy as np
from keras.models import load_model
from keras.utils import pad_sequences
import threading

app = Flask(__name__)

# Load model & artifacts at startup (non-blocking)
model = None
tokenizer = None
lbl_encoder = None
intents = None
model_ready = False

def load_resources():
    """Load resources in background to prevent blocking"""
    global model, tokenizer, lbl_encoder, intents, model_ready
    model = load_model("chat_model/chat_model.keras")
    with open("chat_model/tokenizer.pickle","rb") as f:
        tokenizer = pickle.load(f)
    with open("chat_model/label_encoder.pickle","rb") as f:
        lbl_encoder = pickle.load(f)
    with open("intents.json","r", encoding="utf-8") as f:
        intents = json.load(f)
    model_ready = True

# Load resources in background thread
loading_thread = threading.Thread(target=load_resources, daemon=True)
loading_thread.start()

MAX_LEN = 20

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    # Wait if model is still loading
    if not model_ready:
        return jsonify({"reply": "Model is loading, please wait..."}), 503
    
    user_msg = request.form.get("message", "").strip()
    
    # Quick validation
    if not user_msg or len(user_msg) > 500:
        return jsonify({"reply": "Invalid message."}), 400
    
    # Tokenize and predict
    seq = tokenizer.texts_to_sequences([user_msg])
    padded = pad_sequences(seq, maxlen=MAX_LEN, truncating="post")
    
    # Use verbose=0 to reduce overhead
    pred = model.predict(padded, verbose=0, batch_size=1)
    tag = lbl_encoder.inverse_transform([np.argmax(pred)])[0]
    
    # Find responses for tag (optimized lookup)
    intent_dict = {intent["tag"]: intent.get("responses", ["Sorry."]) 
                   for intent in intents.get("intents", [])}
    
    response = intent_dict.get(tag, ["Sorry, I didn't understand that."])
    return jsonify({"reply": np.random.choice(response)})

if __name__ == "__main__":
    # Use production server in deployment
    app.run(debug=False, threaded=True)
