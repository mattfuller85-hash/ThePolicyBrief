"""
The Policy Brief - Hourly Congress Check
Runs every hour via GitHub Actions. Fetches recent bills, deduplicates
against previously processed bills, and runs the audit + content pipeline
only when new legislation is found.
"""

import json
import os
import random
import time
from datetime import datetime
from engine import CongressSource, FinancialAuditor, ResendDelivery, ANCHORS
from dotenv import load_dotenv


DATA_DIR = os.path.join(os.path.dirname(__file__), "web", "src", "data")
KNOWN_IDS_PATH = os.path.join(DATA_DIR, "known_bill_ids.json")
AUDITS_PATH = os.path.join(DATA_DIR, "daily_audits.json")
TARGET_EMAIL = "mattfuller85@gmail.com"


def load_known_ids() -> set:
    """Load the set of bill IDs that have already been processed."""
    if os.path.exists(KNOWN_IDS_PATH):
        with open(KNOWN_IDS_PATH, "r") as f:
            return set(json.load(f))
    return set()


def save_known_ids(ids: set):
    """Persist the set of known bill IDs."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(KNOWN_IDS_PATH, "w") as f:
        json.dump(sorted(ids), f, indent=2)


def load_existing_audits() -> list:
    """Load any previously saved audit results."""
    if os.path.exists(AUDITS_PATH):
        with open(AUDITS_PATH, "r") as f:
            return json.load(f)
    return []


def save_audits(audits: list):
    """Save audit results to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(AUDITS_PATH, "w") as f:
        json.dump(audits, f, indent=2)


def run_hourly_check():
    load_dotenv()

    congress_key = os.getenv("CONGRESS_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    resend_key = os.getenv("RESEND_API_KEY")

    if not congress_key:
        print("❌ CONGRESS_API_KEY not set. Exiting.")
        return
    if not gemini_key:
        print("❌ GEMINI_API_KEY not set. Exiting.")
        return

    # --- Step 1: Fetch recent bills ---
    source = CongressSource(api_key=congress_key)
    bills = source.fetch_daily_bills(limit=20)

    if not bills:
        print("ℹ️  No bills returned from Congress API. Exiting.")
        return

    # --- Step 2: Deduplicate ---
    known_ids = load_known_ids()
    new_bills = []
    for bill in bills:
        bill_id = source.get_bill_id(bill)
        if bill_id not in known_ids:
            new_bills.append(bill)

    if not new_bills:
        print(f"✅ No new bills found. All {len(bills)} fetched bills already processed.")
        return

    print(f"🆕 Found {len(new_bills)} new bill(s) to audit!")

    # --- Step 3: Audit each new bill ---
    auditor = FinancialAuditor(api_key=gemini_key)
    existing_audits = load_existing_audits()
    new_audits = []

    for bill in new_bills:
        bill_id = source.get_bill_id(bill)
        bill_title = bill.get("title", "Untitled Bill")
        congress_num = bill.get("congress", 119)
        bill_type = bill.get("type", "hr")
        bill_number = bill.get("number", 0)

        print(f"\n--- Processing [{bill_id}] {bill_title} ---")

        # Fetch bill summary text from Congress API
        summary_text = source.fetch_bill_summary(congress_num, bill_type, bill_number)

        if not summary_text:
            # Fall back to just using the title if no summary is available
            print(f"⚠️  No summary text available for {bill_id}. Using title only.")
            summary_text = f"Bill titled: {bill_title}. No detailed summary text is available from Congress.gov at this time."

        # Run the CoVe two-pass audit (this also generates the blog post + YouTube script)
        anchor = random.choice(ANCHORS)
        audit_result = auditor.audit_bill(summary_text, bill_title, anchor)

        if not isinstance(audit_result, dict):
            print(f"⚠️  Audit returned non-dict for {bill_id}. Skipping.")
            continue

        # Merge metadata
        audit_result["bill_id"] = bill_id
        audit_result["anchor_name"] = anchor["name"]
        audit_result["title"] = bill_title
        audit_result["congress"] = congress_num
        audit_result["processed_at"] = datetime.utcnow().isoformat() + "Z"

        # Sponsor Dox
        sponsor_name = bill.get("sponsors", [{}])[0].get("name", None) if bill.get("sponsors") else None
        if not sponsor_name:
            # Try the latestAction or title for a hint
            sponsor_name = audit_result.get("sponsor_contact_info", {}).get("sponsor_name")
        if sponsor_name:
            audit_result["sponsor_contact_info"] = auditor.dox_sponsor(sponsor_name)

        new_audits.append(audit_result)
        known_ids.add(bill_id)

        # Pace API requests (free-tier Gemini limit)
        print(f"⏳ Pacing between bills...")
        time.sleep(5)

    # --- Step 4: Send email notifications ---
    if resend_key and new_audits:
        delivery = ResendDelivery(resend_key)
        for audit in new_audits:
            print(f"📧 Sending script email for {audit.get('bill_id')}...")
            delivery.deliver_short_script(audit, TARGET_EMAIL)

    # --- Step 5: Persist results ---
    all_audits = existing_audits + new_audits
    save_audits(all_audits)
    save_known_ids(known_ids)

    print(f"\n✅ Hourly check complete! Processed {len(new_audits)} new bill(s).")
    print(f"   Total audits on file: {len(all_audits)}")

    # Log what was generated for visibility
    for audit in new_audits:
        has_blog = bool(audit.get("blog_post_markdown"))
        has_script = bool(audit.get("heygen_short_script"))
        print(f"   [{audit.get('bill_id')}] blog={'✅' if has_blog else '❌'} script={'✅' if has_script else '❌'}")


if __name__ == "__main__":
    run_hourly_check()
