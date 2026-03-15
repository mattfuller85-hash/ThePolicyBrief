import json
import os
from dotenv import load_dotenv
from engine import FinancialAuditor

def main():
    load_dotenv()
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("Missing GEMINI_API_KEY")
        return

    auditor = FinancialAuditor(api_key=gemini_key)

    json_path = os.path.join(os.path.dirname(__file__), "web", "src", "data", "daily_audits.json")
    with open(json_path, "r") as f:
        audits = json.load(f)

    print("Extracting a short script from existing data...")
    short_script = "No fluff_detected == true bill found."
    for audit in audits:
        if audit.get("fluff_detected"):
            short_script = audit.get("heygen_short_script", "Missing short script.")
            break

    print("Generating a long-form daily summary script...")
    long_script, anchor_name = auditor.generate_daily_summary_script(audits)

    output = f"=== SHORT SCRIPT ===\n{short_script}\n\n=== LONG FORM SUMMARY SCRIPT (Anchor: {anchor_name}) ===\n{long_script}\n"
    
    with open("sample_scripts.txt", "w") as f:
        f.write(output)

    print("Done. Saved to sample_scripts.txt")

if __name__ == "__main__":
    main()
