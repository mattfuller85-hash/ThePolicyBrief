import os
from google import genai
from dotenv import load_dotenv

def main():
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=key)
    
    print("Listing ALL available models for this API key:")
    available_models = []
    try:
        for m in client.models.list():
            print(f"- {m.name} (Display: {m.display_name})")
            available_models.append(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
        
    print("\nTesting which of these accept generation requests without limit 0...")
    
    for model_name in available_models:
        if 'flash' in model_name.lower() or 'pro' in model_name.lower():
            if 'vision' in model_name.lower() or 'embedding' in model_name.lower():
                continue
            print(f"Testing {model_name}...")
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents='Say hi'
                )
                print(f"✅ Success! Generated: {response.text}")
            except Exception as e:
                msg = str(e)
                if 'limit: 0' in msg:
                    print("❌ Failed: Hard limit of 0")
                else:
                    print(f"❌ Failed: {type(e).__name__} - {msg[:100]}...")

if __name__ == "__main__":
    main()
