import os
from google import genai
from dotenv import load_dotenv

def main():
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=key)
    
    models_to_test = [
        'gemini-2.5-flash',
        'gemini-2.0-flash', 
        'gemini-2.0-flash-lite-preview-02-05',
        'gemini-1.5-flash', 
        'gemini-1.5-pro',
        'gemini-1.5-flash-8b'
    ]
    
    for model in models_to_test:
        print(f"Testing {model}...")
        try:
            response = client.models.generate_content(
                model=model,
                contents='Say hello'
            )
            print(f"✅ Success! Generated: {response.text}")
        except Exception as e:
            msg = str(e)
            if 'limit: 0' in msg:
                print("❌ Failed: Hard limit of 0")
            elif '404' in msg or 'not found' in msg.lower():
                print("❌ Failed: Model not found")
            else:
                print(f"❌ Failed: {type(e).__name__} - {msg[:100]}...")
        print("-" * 40)

if __name__ == "__main__":
    main()
