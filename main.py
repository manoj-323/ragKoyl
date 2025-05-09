import json
import requests
import chromadb

from sentence_transformers import SentenceTransformer



URL = 'http://localhost:11434/api/generate'
HEADERS = {
        'Content-Type': 'application/json'
    }

# load the higging face text embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# wrapper class as chromadb do not natively support hugging face models
class SentenceTransformerEmbeddingFunction:
    """
    Wrapper function for SentenceTransformer hugging face model for chromadb.
    """
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
    """
    Takes in a user query and generates a response through RAG (Retrieval-Augmented Generation) architecture.

    Args:
        question (str): user query.
    
    Returns:
        str: response to user query.
    """
    context_res = collection.query(
        query_texts=[question],
        n_results=5
    )
    context = ' '.join(context_res['documents'][0])

    print(context, '\n\n')

    data = {
        'model': 'deepseek-r1:1.5b',
        'prompt': f"You are a helpful doctor. I want you to help me figure out nutitions required accoding to my current symptoms. Use this context as base to answer:\n\n{context}\n\nQuestion: {question}",
        'stream': False
    }

    res = requests.post(URL, headers=HEADERS, data=json.dumps(data))

    if res.status_code == 200:
        res_text = res.text
        data = json.loads(res_text)
        actual_res = data['response']
        return actual_res
    
    return 'Some error occured!:- ' + res.status_code


question = "What are the nutrition recommendations for managing anxiety?"
answer = generate_response(question)

print("\n======== Final Answer ========\n")
print(answer)