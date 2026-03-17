import os
import json
from dotenv import load_dotenv
from engine import FinancialAuditor

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

auditor = FinancialAuditor(api_key=api_key)

mock_bill_title = "National 4-H Week Resolution"
mock_bill_text = "This resolution supports the designation of October 5-11, 2025, as National 4–H Week and recognizes the important role of 4–H. No funds are appropriated."

print("\nExecuting CoVe Pipeline...")
audit_result = auditor.audit_bill(mock_bill_text, mock_bill_title, anchor=None, sponsor_name="Committee on Agriculture")

print("\n--- RESULTS JSON ---")
print(json.dumps(audit_result, indent=2))
