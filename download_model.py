import os
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
SAVE_PATH = "models/all-MiniLM-L6-v2"

print("Starting embedding model download...")

os.makedirs(SAVE_PATH, exist_ok=True)

model = SentenceTransformer(MODEL_NAME)

print("Model downloaded successfully.")

model.save(SAVE_PATH)

print(f"Model saved successfully at:")
print(os.path.abspath(SAVE_PATH))