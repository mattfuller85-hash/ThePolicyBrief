"""
The Policy Brief - Congress Check (5-Minute Interval)
Runs every 5 minutes via GitHub Actions. Fetches recent bills, deduplicates
against previously processed bills, and runs the audit + content pipeline
only when new legislation is found.
"""

import json
import os
import random
import time
from datetime import datetime, timezone
from engine import CongressSource, FinancialAuditor, ResendDelivery, ANCHORS
from dotenv import load_dotenv


DATA_DIR = os.path.join(os.path.dirname(__file__), "web", "src", "data")
KNOWN_IDS_PATH = os.path.join(DATA_DIR, "known_bill_ids.json")
AUDITS_PATH = os.path.join(DATA_DIR, "daily_audits.json")
TARGET_EMAIL = "mattfuller85@gmail.com"

# Process at most this many bills per 5-minute run to stay within
# Gemini free-tier rate limits (15 RPM).
MAX_BILLS_PER_RUN = 1


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


def run_5min_check():
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

    # --- Force Reset Override ---
    force_reset = os.getenv("FORCE_RESET", "no").lower() == "yes"
    if force_reset:
        print("🔄 FORCE RESET enabled! Clearing known bills and audit data...")
        save_known_ids(set())
        save_audits([])

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

    # Cap to MAX_BILLS_PER_RUN per run; the rest will be caught next run
    bills_to_process = new_bills[:MAX_BILLS_PER_RUN]
    remaining = len(new_bills) - len(bills_to_process)
    print(f"🆕 Found {len(new_bills)} new bill(s). Processing {len(bills_to_process)} this run.")
    if remaining > 0:
        print(f"   ⏭️  {remaining} bill(s) deferred to next run.")

    # --- Step 3: Audit each new bill ---
    auditor = FinancialAuditor(api_key=gemini_key)
    existing_audits = load_existing_audits()
    new_audits = []

    for i, bill in enumerate(bills_to_process):
        bill_id = source.get_bill_id(bill)
        bill_title = bill.get("title", "Untitled Bill")
        congress_num = bill.get("congress", 119)
        bill_type = bill.get("type", "hr")
        bill_number = bill.get("number", 0)

        print(f"\n--- Processing [{bill_id}] {bill_title} ---")

        # Fetch full bill details to get the sponsors
        bill_details = source.fetch_bill_details(congress_num, bill_type, bill_number)
        
        # Try to fetch full formatted text first
        bill_text = source.fetch_bill_text(congress_num, bill_type, bill_number)
        
        if not bill_text:
            print(f"⚠️  No full text available for {bill_id}. Falling back to summary.")
            bill_text = source.fetch_bill_summary(congress_num, bill_type, bill_number)
        else:
            print(f"✅ Full text retrieved for {bill_id}.")

        # Fetch bill actions & related bills for history
        actions = source.fetch_bill_actions(congress_num, bill_type, bill_number)
        related = source.fetch_related_bills(congress_num, bill_type, bill_number)
        
        history_context = "\n\n--- BILL HISTORY & STATUS ---\n"
        if actions:
            history_context += "Recent Actions & Vote Status:\n"
            for action in actions[:5]: # just the 5 most recent to save tokens
                history_context += f"- {action.get('actionDate', 'Unknown Date')}: {action.get('text', 'Unknown Action')}\n"
        else:
            history_context += "Recent Actions: Not available.\n"
            
        if related:
            history_context += f"Previously Proposed: Yes, {len(related)} related/previous bills found.\n"
        else:
            history_context += "Previously Proposed: No (This appears to be the first time this bill is proposed).\n"

        if not bill_text:
            # Fall back to just using the title if no text or summary is available
            print(f"⚠️  No text or summary available for {bill_id}. Using title only.")
            bill_text = f"Bill titled: {bill_title}. No detailed text or summary is available from Congress.gov at this time."
            
        bill_text += history_context

        # Extract Sponsor Name from full details
        sponsor_name = None
        sponsors = bill_details.get("sponsors", [])
        if sponsors:
            sponsor_name = sponsors[0].get("fullName")

        # Run the CoVe two-pass audit (this also generates the blog post + YouTube script)
        anchor = random.choice(ANCHORS)
        audit_result = auditor.audit_bill(bill_text, bill_title, anchor, sponsor_name=sponsor_name, bill_id=bill_id)

        if not isinstance(audit_result, dict) or "heygen_short_script" not in audit_result or not audit_result["heygen_short_script"]:
            print(f"⚠️  Audit result is empty or invalid for {bill_id} (API failure). Skipping.")
            continue

        # Merge metadata
        audit_result["bill_id"] = bill_id
        audit_result["anchor_name"] = anchor["name"]
        audit_result["title"] = bill_title
        audit_result["congress"] = congress_num
        audit_result["processed_at"] = datetime.now(timezone.utc).isoformat()

        # Sponsor Dox
        if not sponsor_name:
            # Try the latestAction or title for a hint
            sponsor_name = audit_result.get("sponsor_contact_info", {}).get("sponsor_name")
        if sponsor_name:
            audit_result["sponsor_contact_info"] = auditor.dox_sponsor(sponsor_name)

        new_audits.append(audit_result)
        known_ids.add(bill_id)

    # --- Step 4: Send email notifications ---
    if resend_key and new_audits:
        delivery = ResendDelivery(resend_key)
        for i, audit in enumerate(new_audits):
            print(f"📧 Sending script email for {audit.get('bill_id')}...")
            delivery.deliver_short_script(audit, TARGET_EMAIL, thumbnail_path=None)

    # --- Step 5: Persist results ---
    all_audits = existing_audits + new_audits
    save_audits(all_audits)
    save_known_ids(known_ids)

    print(f"\n✅ Check complete! Processed {len(new_audits)} new bill(s).")
    print(f"   Total audits on file: {len(all_audits)}")

    # Log what was generated for visibility
    for audit in new_audits:
        has_blog = bool(audit.get("blog_post_markdown"))
        has_script = bool(audit.get("heygen_short_script"))
        print(f"   [{audit.get('bill_id')}] blog={'✅' if has_blog else '❌'} script={'✅' if has_script else '❌'}")


if __name__ == "__main__":
    run_5min_check()
