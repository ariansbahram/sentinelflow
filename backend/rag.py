import json
import os
import faiss
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY, EMBEDDING_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

BASE_DIR = os.path.dirname(__file__)
CASE_PATH = os.path.join(BASE_DIR, "data", "historical_cases.json")

def load_cases():
    with open(CASE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def case_to_text(case):
    return (
        f"Type: {case['type']}. "
        f"Content: {case['content']} "
        f"Summary: {case['summary']} "
        f"Severity: {case['severity']} "
        f"Outcome: {case['outcome']}"
    )

def get_embedding(text: str) -> np.ndarray:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return np.array(response.data[0].embedding, dtype="float32")

class CaseRetriever:
    def __init__(self):
        self.cases = load_cases()
        self.texts = [case_to_text(case) for case in self.cases]
        self.embeddings = np.array([get_embedding(text) for text in self.texts], dtype="float32")
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(self.embeddings)

    def retrieve(self, query: str, k: int = 2):
        query_embedding = get_embedding(query).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, k)
        results = []

        for idx, dist in zip(indices[0], distances[0]):
            case = self.cases[idx]
            results.append({
                "id": case["id"],
                "type": case["type"],
                "summary": case["summary"],
                "severity": case["severity"],
                "outcome": case["outcome"],
                "distance": float(dist)
            })

        return results
