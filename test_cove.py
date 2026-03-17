import json
import os
from dotenv import load_dotenv

load_dotenv()

from engine import FinancialAuditor, ANCHORS

auditor = FinancialAuditor(api_key=os.getenv("GEMINI_API_KEY"))
mock_bill_title = "The Community Bridge and Coy Fish Pond Act of 2024"
mock_bill_text = "This bill allocates $30,000,000 for the construction of a new suspension bridge connecting the two main commercial districts. Additionally, a rider has been attached to allocate $5,000,000 for a luxury coy fish pond in the mayor's backyard, completely unrelated to the bridge infrastructure."

print("Running Audit...")
audit = auditor.audit_bill(mock_bill_text, mock_bill_title, ANCHORS[0], "Mayor Smith", "HR123")
print("\n---heygen_short_script---")
print(audit.get('heygen_short_script'))
