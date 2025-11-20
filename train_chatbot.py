import json
import numpy as np
import pickle
from pathlib import Path

# TensorFlow/Keras imports
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, GlobalAveragePooling1D, Dense

# Load intents
with open("intents.json", "r", encoding="utf-8") as f:
    data = json.load(f)

training_sentences = []
training_labels = []
labels = []
responses = {}

for intent in data['intents']:
    tag = intent['tag']
    responses[tag] = intent.get('responses', [])
    for pattern in intent['patterns']:
        training_sentences.append(pattern)
        training_labels.append(tag)
    if tag not in labels:
        labels.append(tag)

num_classes = len(labels)

# Encode labels
lbl_encoder = LabelEncoder()
lbl_encoder.fit(training_labels)
training_labels_enc = lbl_encoder.transform(training_labels)

# Tokenizer
vocab_size = 1000
embedding_dim = 16
max_len = 20
oov_token = "<OOV>"

tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_token)
tokenizer.fit_on_texts(training_sentences)
sequences = tokenizer.texts_to_sequences(training_sentences)
padded = pad_sequences(sequences, truncating='post', maxlen=max_len)

# Model
model = Sequential([
    Embedding(vocab_size, embedding_dim, input_length=max_len),
    GlobalAveragePooling1D(),
    Dense(32, activation='relu'),
    Dense(num_classes, activation='softmax')
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

print("Training model...")
model.fit(padded, np.array(training_labels_enc), epochs=400, verbose=1)

# Save model and artifacts
model.save("chat_model/chat_model.keras")

with open("chat_model/tokenizer.pickle", "wb") as f:
    pickle.dump(tokenizer, f)

with open("chat_model/label_encoder.pickle", "wb") as f:
    pickle.dump(lbl_encoder, f)

print("Saved: chat_model.keras, tokenizer.pickle, label_encoder.pickle")


