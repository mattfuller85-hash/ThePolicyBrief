import json
import os
import random
import time
from engine import FinancialAuditor, ResendDelivery, ANCHORS
from dotenv import load_dotenv
from datetime import datetime

# Provide some mock bills for the pipeline to process, since fetching full text 
# from Congress API requires multiple endpoints and XML parsing.
MOCK_BILLS = [
    {
        "id": "HR1042",
        "title": "The Community Bridge and Coy Fish Pond Act of 2026",
        "text": "This bill allocates $30,000,000 for the construction of a new suspension bridge connecting the two main commercial districts. Additionally, a rider has been attached to allocate $5,000,000 for a luxury coy fish pond in the mayor's backyard, completely unrelated to the bridge infrastructure.",
        "sponsor": "Senator Elizabeth Warren"
    },
    {
        "id": "S402",
        "title": "Defense Procurement and Tactical Gear Act",
        "text": "Allocates $800,000,000 for standard tactical gear upgrades. Includes a $200,000,000 provision for 'classified entertainment expenses' directed to a private club, completely unrelated to military functionality.",
        "sponsor": "Senator Ted Cruz"
    },
    {
        "id": "HR2099",
        "title": "National Parks and Rejuvenation Act of 2026",
        "text": "This bill provides $150,000,000 for the maintenance and upkeep of Yellowstone National Park. It also sneaks in a $12,000,000 grant to build a private helicopter pad for a billionaire donor's nearby ranch under the guise of 'emergency access'.",
        "sponsor": "Representative Alexandria Ocasio-Cortez"
    },
    {
        "id": "S890",
        "title": "The Future of AI Innovation and Education Bill",
        "text": "Grants $50,000,000 to public high schools to purchase new laptops and AI software. However, $8,000,000 of the funds are earmarked for a vague 'AI Ethics Consulting' firm that was formed last week by the sponsor's nephew.",
        "sponsor": "Senator Chuck Schumer"
    },
    {
        "id": "HR551",
        "title": "Rural Healthcare Expansion Initiative",
        "text": "Provides $200,000,000 to build 10 new rural medical clinics in underserved counties. It additionally includes $30,000,000 to renovate a golf course in the capital city because it is 'vital for the mental health of healthcare executives'.",
        "sponsor": "Senator Mitch McConnell"
    }
]

def run_pipeline():
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("GEMINI_API_KEY not found. Please add it to your .env file.")
        return
        
    resend_key = os.getenv("RESEND_API_KEY")
    TARGET_EMAIL = "mattfuller85@gmail.com" # TODO: Make this an env var if needed later
    
    if not resend_key:
        print("RESEND_API_KEY not found. Please add it to your .env file.")
        return
        
    resend_delivery = ResendDelivery(resend_key)

    auditor = FinancialAuditor(gemini_key)
    
    audits = []
    
    print("Starting The Policy Brief Pipeline...")
    
    for bill in MOCK_BILLS[:2]:
        print(f"Auditing [{bill['id']}] {bill['title']}...")
        anchor = random.choice(ANCHORS)
        result = auditor.audit_bill(bill['text'], bill['title'], anchor)
        print("DEBUG RESULT:", result)
        
        # Make sure the result is a dict (if the API fails or returns something else, we handle it)
        if not isinstance(result, dict):
            print("Result was not a dict! Changing to empty dict.")
            result = {}
            
        # Merge ID, Anchor, and Sponsor Dox
        result['bill_id'] = bill['id']
        result['anchor_name'] = anchor['name']
        
        sponsor_info = auditor.dox_sponsor(bill['sponsor'])
        result['sponsor_contact_info'] = sponsor_info
        
        audits.append(result)
        
        print(f"Delivering Short Script for {bill['id']} via Resend...")
        resend_delivery.deliver_short_script(result, TARGET_EMAIL)
        
        print("Waiting 60 seconds before processing the next bill to pace API requests...")
        time.sleep(60)
        
    print(f"Generating Summary Script for {len(audits)} audited bills...")
    summary_script, summary_anchor = auditor.generate_daily_summary_script(audits)
    
    print("Delivering Nightly Summary via Resend...")
    # Wrap the returned summary script text into a basic dictionary for the delivery method
    # Since we updated the prompt to return JSON, `summary_script` should actually be a dict now.
    # If not, we will handle it.
    if isinstance(summary_script, str):
        try:
            summary_data = json.loads(summary_script)
        except json.JSONDecodeError:
            # Fallback if Gemini failed to return strict JSON
            summary_data = {"title": "Daily Policy Brief Summary", "script_body": summary_script}
    else:
        summary_data = summary_script
        
    resend_delivery.deliver_daily_summary(summary_data, summary_anchor, TARGET_EMAIL)
    
    for audit in audits:
        audit['emailed'] = True
        
    output_dir = os.path.join(os.path.dirname(__file__), "web", "src", "data")
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "daily_audits.json")
    
    with open(out_path, "w") as f:
        json.dump(audits, f, indent=2)
        
    print(f"✅ Pipeline complete! Saved {len(audits)} audited bills to {out_path}")

if __name__ == "__main__":
    run_pipeline()
