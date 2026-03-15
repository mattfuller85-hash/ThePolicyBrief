# Data Schema & Prompts (V7 Investigative Auditor Standards)

## 0. Legal & Persona (The 'Neutral Auditor')
The AI must adopt a 'Neutral Auditor' persona at all times.
- **Tone:** Objective, clinical, and fact-based.
- **Restrictions:** Strict avoidance of partisan adjectives (e.g., 'reckless', 'corrupt', 'draconian').
- **Standard:** Reframe subjective claims into factual observations (e.g., 'unrelated to bill title', 'diverges from primary stated purpose').

## 1. financial_audit (Pork Itemization & V7 Verification)
Schema for extracting and verifying spending amounts from bill text using the strict two-pass Prosecutor (CoVe) method.
```json
{
  "bill_id": "String",
  "date_proposed": "String (YYYY-MM-DD)",
  "historical_context": "String (Brief context on why the bill was introduced)",
  "total_spending": "Number",
  "legitimate_spending": "Number (Spending directly related to the stated title/purpose of the bill)",
  "pork_barrel_spending": "Number (Spending directed to specific interests, unrelated to the core purpose)",
  "pork_to_value_ratio": "Number (Percentage of total spending designated as pork)",
  "fluff_detected": "Boolean",
  "fluff_items": [
    "String (Description of unrelated rider or earmark, e.g., the 'Coy fish pond' test)"
  ],
  "sponsor_contact_info": {
    "sponsor_name": "String",
    "phone_number": "String",
    "website": "String",
    "social_handles": {
      "twitter": "String",
      "facebook": "String",
      "instagram": "String"
    }
  },
  "heygen_short_script": "String (High-energy 30s script focusing on the most shocking pork item)",
  "heygen_long_script": "String (Deep dive 10m YouTube script: history, legitimate spending, and pork breakdown)",
  "youtube_metadata": {
    "title": "String",
    "tags": ["String"],
    "copyright": "String ('© 2024 The Policy Brief, LLC')"
  }
}
```

## 2. thumbnail_assets
Schema for the Adaptive Thumbnail & Blog Image Engine.
```json
{
  "image_prompt": "String (A detailed prompt for Imagen/Gemini to generate a high-quality thematic visual)",
  "adaptive_branding_logic": {
    "fluff_detected": "Boolean",
    "overlay_text": "String ('PORK ALERT' or 'BILL BRIEF')",
    "brand_colors": "String ('Red/Yellow' or 'Blue/Gold')"
  }
}
```

## 3. newsletter_html
Schema for the Weekly Briefing Friday script (The Value Audit / Pork Leaderboard).
```json
{
  "subject": "The Policy Brief: The Weekly Value Audit",
  "html_body": "String (Responsive HTML containing the top 5 'Pork-Filled' bills on the Pork Leaderboard, total weekly spending, and actionable contact information for sponsors)"
}
```
