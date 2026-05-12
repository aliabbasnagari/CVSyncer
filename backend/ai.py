import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_API_BASE_URL") 
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

print("Model:", MODEL)

prompt = "What is the capital of France?"

print("Prompt:", prompt)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL) if BASE_URL else OpenAI(api_key=API_KEY)

response = client.responses.create(
    model=MODEL,
    input=prompt
)

print("Response:", response.output_text)

"""
response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

print("Response:", response.choices[0].message.content)
"""