import json
import requests
import chromadb
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer
from flask_cors import CORS


app = Flask(__name__)

CORS(app)

URL = 'http://localhost:11434/api/generate'
HEADERS = {'Content-Type': 'application/json'}

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

class SentenceTransformerEmbeddingFunction:
    def __init__(self, model):
        self.model = model
    def __call__(self, input):
        return self.model.encode(input).tolist()

embedding_function = SentenceTransformerEmbeddingFunction(embedding_model)

chroma_client = chromadb.PersistentClient(path="chroma_persistent_storage")
collection = chroma_client.get_or_create_collection(
    name="medical_chunks",
    embedding_function=embedding_function
)

def generate_response(question: str) -> str:
    try:
        context_res = collection.query(query_texts=[question], n_results=5)
        context = ' '.join(context_res['documents'][0])

        prompt = f"You are a helpful doctor. I want you to help me figure out nutrition required according to my current symptoms. Use this context as base to answer:\n\n{context}\n\nQuestion: {question}"

        data = {
            'model': 'deepseek-r1:1.5b',
            'prompt': prompt,
            'stream': False
        }

        res = requests.post(URL, headers=HEADERS, data=json.dumps(data))
        if res.status_code == 200:
            print(context,  '\n\n', json.loads(res.text)['response'])
            return context, json.loads(res.text)['response']
        return f"Error from model: {res.status_code}"
    except Exception as e:
        return f"Exception: {str(e)}"


@app.route('/query', methods=['POST'])
def handle_query():
    req_data = request.get_json()
    question = req_data.get("question", "")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    context, answer = generate_response(question)
    return jsonify({"question": question, "answer": answer, "context": context})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
