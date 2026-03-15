import json
import os
from engine import GoogleDocDelivery
from dotenv import load_dotenv

def test_docs():
    load_dotenv()
    google_creds_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS")
    google_doc_id = os.getenv("GOOGLE_DOC_ID")
    doc_delivery = GoogleDocDelivery(google_creds_path, google_doc_id)

    # load the first mock audit
    with open('web/src/data/daily_audits.json', 'r') as f:
        audits = json.load(f)
        
    if audits:
        result = audits[0]
        doc_link = doc_delivery.deliver_daily_scripts(result)
        print("Generated Link:", doc_link)

if __name__ == "__main__":
    test_docs()
