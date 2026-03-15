import os
import resend
from dotenv import load_dotenv

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

try:
    r = resend.Emails.send({
        "from": "Acme <onboarding@resend.dev>",
        "to": "mattfuller85@gmail.com",
        "subject": "Test Email from The Policy Brief",
        "html": "<h2>It works!</h2><p>The case sensitivity issue is fixed.</p>"
    })
    print("✅ Delivered Test Script")
except Exception as e:
    print(f"❌ Resend API Error: {e}")
