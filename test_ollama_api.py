import re
import json
import requests

url = 'http://localhost:11434/api/generate'

headers = {
    'Content-Type': 'application/json'
}

data = {
    'model': 'deepseek-r1:1.5b',
    'prompt': 'What are the nutrition recommendations for managing anxiety?',
    'stream': False
}

res = requests.post(url, headers=headers, data=json.dumps(data))

if res.status_code == 200:
    res_text = res.text
    data = json.loads(res_text)
    actual_res = data['response']
    print(actual_res)
else:
    print("error: ", res.status_code, res.text)