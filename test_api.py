import traceback, sys, os
sys.path.insert(0, r'e:\Product cá nhân\KHTN SONG NGỮ\KHTNSongNgu')
os.chdir(r'e:\Product cá nhân\KHTN SONG NGỮ\KHTNSongNgu')

# Test 1: Check API key and model
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")
model_name = os.getenv("GENERATION_MODEL", "gemma-3-4b-it")
print(f"API Key: {api_key[:10]}...{api_key[-5:]}")
print(f"Model: {model_name}")

# Test 2: Try Gemini API call
import google.generativeai as genai
genai.configure(api_key=api_key)

print("\n--- Test non-streaming ---")
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say hello in 5 words")
    print("OK:", response.text[:100])
except Exception as e:
    print(f"ERROR: {e}")

print("\n--- Test streaming ---")
try:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say hello in 5 words", stream=True)
    for chunk in response:
        if chunk.text:
            print(f"CHUNK: {chunk.text[:50]}")
    print("Streaming OK!")
except Exception as e:
    print(f"STREAM ERROR: {e}")
    traceback.print_exc()

# Test 3: Try known good model
print("\n--- Test with gemini-2.0-flash ---")
try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Say hello", stream=True)
    for chunk in response:
        if chunk.text:
            print(f"CHUNK: {chunk.text[:50]}")
    print("gemini-2.0-flash OK!")
except Exception as e:
    print(f"ERROR: {e}")
