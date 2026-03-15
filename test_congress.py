import os
import requests
from dotenv import load_dotenv

def test_congress_api():
    """Simple connection test for the Congress.gov v3 API."""
    load_dotenv()
    api_key = os.getenv("CONGRESS_API_KEY")
    
    if not api_key:
        print("❌ Error: CONGRESS_API_KEY not found in .env file.")
        return

    print("Testing Congress.gov API Connection...")
    
    # We'll fetch the most recent bills from the current Congress (118)
    url = f"https://api.congress.gov/v3/bill/118?api_key={api_key}&limit=5"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        
        data = response.json()
        bills = data.get("bills", [])
        
        print(f"✅ Connection Successful! Fetched {len(bills)} recent bills.\n")
        
        for i, bill in enumerate(bills):
            print(f"[{i+1}] {bill.get('type')} {bill.get('number')} - {bill.get('title')}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_congress_api()
