import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

def test_prompt():
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)
    
    prompt = """
    You are an expert scriptwriter.
    Write a 30s-2m YouTube Short script for a news anchor based on the following bill.
    
    Bill ID: HR1042
    Title: The Community Bridge and Coy Fish Pond Act of 2026
    Sponsor: Representative Tim Daily
    Text: This bill allocates $30,000,000 for the construction of a new suspension bridge connecting the two main commercial districts. Additionally, a rider has been attached to allocate $5,000,000 for a luxury coy fish pond in the mayor's backyard, completely unrelated to the bridge infrastructure.
    
    CRITICAL INSTRUCTION:
    You MUST start the script with the EXACT structure:
    'Bill HR1042 proposed by Representative Tim Daily today is requesting a $35,000,000 allocation for "The Community Bridge and Coy Fish Pond Act of 2026".'
    
    After the intro, discuss the surface-level promise, the glaring anomaly (the coy fish pond fluff), the pork-to-value ratio, and explicitly state who the winners and losers are. Be creative and engaging. Do not use generic greetings.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        print("--- GENERATED SHORT SCRIPT ---")
        print(response.text)
        print("------------------------------")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_prompt()
