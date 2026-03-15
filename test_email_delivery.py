import json
import os
from dotenv import load_dotenv
from engine import ResendDelivery, FinancialAuditor

def main():
    load_dotenv()
    resend_key = os.getenv("RESEND_API_KEY")
    TARGET_EMAIL = "mattfuller85@gmail.com"

    if not resend_key:
        print("Missing RESEND_API_KEY")
        return

    json_path = os.path.join(os.path.dirname(__file__), "web", "src", "data", "daily_audits.json")
    with open(json_path, "r") as f:
        audits = json.load(f)

    # Short Script
    print("Testing Short Script Email Delivery (The Policy Brief)...")
    short_target = None
    for audit in audits:
        if audit.get("fluff_detected"):
            short_target = audit
            break
            
    resend_del = ResendDelivery(resend_key)
    if short_target:
        resend_del.deliver_short_script(short_target, TARGET_EMAIL)
    else:
        print("No fluff bill found for short script.")

    # Long-Form Summary
    print("Sending Long-form Daily Summary Email Delivery (The Policy Brief)...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        auditor = FinancialAuditor(api_key=gemini_key)
        # Mock just two bills to avoid hitting limits or taking too long
        summary_data, anchor = auditor.generate_daily_summary_script(audits[:2])
        if summary_data:
            resend_del.deliver_daily_summary(summary_data, anchor, TARGET_EMAIL)
        else:
            print("Failed to generate summary.")
    else:
        print("Missing Gemini API Key, cannot generate summary.")

    print("Done! Both emails should be delivered.")

if __name__ == "__main__":
    main()
