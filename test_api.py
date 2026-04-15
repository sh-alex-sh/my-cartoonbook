import requests
import json

api_key = "sk-f487ecd9b1954f85a059ed72bc7b38c9"
url = "https://api.deepseek.com/chat/completions"

payload = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 50
}

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

try:
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")