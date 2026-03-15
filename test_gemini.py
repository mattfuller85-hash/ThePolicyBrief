import os
from google import genai
from dotenv import load_dotenv

def test_gemini_api():
    """Simple connection test for the Gemini API."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file.")
        return

    print("Testing Gemini API Connection using google-genai...")
    
    try:
        client = genai.Client(api_key=api_key)
        # Using a fast, lightweight model for the connection test
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Hello! This is a simple connection test. Please reply with just the word 'Connected!'."
        )
        
        print(f"✅ Connection Successful! Gemini says: {response.text.strip()}")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_gemini_api()
