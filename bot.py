import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

print("--- 사용 가능한 모델 목록 ---")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
print("---------------------------")
