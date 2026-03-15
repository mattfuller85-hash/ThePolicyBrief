import os
import json
from dotenv import load_dotenv
from engine import FinancialAuditor, ResendDelivery

def main():
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    resend_key = os.getenv("RESEND_API_KEY")
    TARGET_EMAIL = "mattfuller85@gmail.com"

    if not gemini_key or not resend_key:
        print("Missing API keys")
        return

    auditor = FinancialAuditor(api_key=gemini_key)
    resend_del = ResendDelivery(resend_key)

    mock_bill_title = "The Rural Healthcare Expansion Initiative"
    mock_bill_id = "HR551"
    mock_bill_text = f"This bill {mock_bill_id} allocates $200,000,000 for the construction of ten new medical clinics in underserved rural counties. Additionally, a rider has been attached to allocate $30,000,000 for a luxury golf course in the capital city, justified as 'vital for the mental health of healthcare executives'."
    
    anchor = {
        "name": "Chloe Kim",
        "vibe": "The Gen-Z/Millennial political outsider. Highly relatable, uses modern pacing, treats bills like ridiculous pop-culture drama."
    }

    print("Auditing mock bill with new prompt...")
    # NOTE: We pass the explicit bill title here so the prompt has access to it
    audit_result = auditor.audit_bill(mock_bill_text, mock_bill_title, anchor=anchor)
    
    audit_result['bill_id'] = mock_bill_id
    audit_result['anchor_name'] = anchor['name']

    print("Generated Short Script:")
    print(audit_result.get("heygen_short_script", "No script generated."))

    print("\nEmailing test script...")
    resend_del.deliver_short_script(audit_result, TARGET_EMAIL)
    print("Done!")

if __name__ == "__main__":
    main()
