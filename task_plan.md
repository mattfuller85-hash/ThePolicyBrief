# The Policy Brief - Task Plan & Roadmap

## Phase 1: The North Star (Blueprint)
- [ ] **The Investigative Radar (Daily Audit)**
  - [ ] Fetch daily bills, voting records, and sponsor info using a combination of Congress.gov, ProPublica, and GovTrack APIs.
  - [ ] Financial Auditor: Itemize dollar amounts, classify spending as "Legitimate" or "Pork-Barrel", and identify "Fluff" (unrelated riders/earmarks).
  - [ ] Sponsor Dox: Use the OpenSecrets API to map the "money trail" (top donors/industries) to the bill's sponsors, supplemented by Google Search grounding for contact info.
- [ ] **The Content Factory (Tiered Video & Imagery)**
  - [ ] The Digital Desktop (Google Docs Delivery): Auto-create a new Google Doc every morning containing HeyGen scripts, shorts scripts, and YouTube metadata.
  - [ ] Adaptive Thumbnail & Blog Image Engine: Use AI (Imagen/Gemini) to generate high-quality thematic visuals for the right side of the image. Use Python (PIL/Pillow) to apply the "Master Template".
    - `fluff_detected == true`: Overlay "PORK ALERT" in high-contrast red/yellow branding alongside the Bill ID.
    - `fluff_detected == false`: Overlay "BILL BRIEF" or "LEGISLATIVE UPDATE" in neutral brand colors alongside the Bill ID.
- [ ] **The Web Hub (Astro/Next.js)**
  - [ ] Auto-rebuild when JSON files are committed to GitHub.
  - [ ] Bento Dashboard: Display "Total Daily Spending" and the "Wall of Shame" (Weekly Pork Leaderboard).
  - [ ] Visual-First Layout: Every post features the AI-generated adaptive thumbnail as the header.
- [ ] **The Weekly Briefing (Newsletter)**
  - [ ] Automated Friday script to aggregate the top 5 "Pork-Filled" bills and send a responsive HTML newsletter via Resend.

## Phase 2: The "Link" Phase (Integrations)
- [ ] Map environment variables:
  - `CONGRESS_API_KEY`
  - `PROPUBLICA_API_KEY`
  - `OPENSECRETS_API_KEY`
  - `GEMINI_API_KEY`
  - `YOUTUBE_API_KEY`
  - `RESEND_API_KEY`
  - `GOOGLE_DRIVE_CREDENTIALS`

## Phase 3: The "Architect" Phase (Core Logic)
- [ ] `engine.py`: Build modular classes for `CongressSource`, `FinancialAuditor` (V7 Investigative Auditor Standards with CoVe 2-pass Verification and strict determinism), `ThumbnailGenerator` (with conditional text logic), `GoogleDocDelivery`, and `ResendMessenger`.
- [ ] Incorporate comprehensive Sponsor Doxing (Phone, Website, Socials) via Google Search Grounding.
- [ ] `crawler.py`: Build automated YouTube URL mapping logic for the "Backwash" effect.

## Phase 4: The "Stylize" Phase (Aesthetics)
- [ ] Web Hub: High-contrast, authoritative "Financial War Room" style.
- [ ] Thumbnail Template: Consistent 70/30 split.
- [ ] Fix the thumbnails for each video (user request).
- [ ] Dynamic Overlay: Branding changes from "Pork Alert" (Red) to "Official Brief" (Blue/Gold) based on audit findings.
- [ ] Brand Voice: Unapologetic, transparent, and objective. "The People's Money."

## Phase 5: Deploy (The "Trigger" Phase)
- [ ] Initialize Git repository and push to GitHub.
- [ ] Generate GitHub Action for the 3:00 AM Daily Run.
- [ ] Generate GitHub Action for the Friday Newsletter Blast.
  - **NODE 20 DEPRECATION NOTE:** To suppress the Node.js 20 warnings in GitHub actions (for checkout@v4 and setup-python@v5), always add `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"` to the main `env:` block. The `true` value MUST be wrapped in quotes so GitHub parses it as a string, preventing the deprecation warnings from persisting.
- [ ] Deploy Astro Web Hub to Vercel.

## Phase 6: Tagging, Filtering & Discoverability
- [ ] **Interest Group / Industry Tags**
  - [ ] Have Gemini identify affected industries/interest groups during the audit and output them as tags (e.g., "Healthcare", "Defense", "Education", "Agriculture").
  - [ ] Store tags in the audit JSON alongside each bill.
  - [ ] Display tags on each blog post as clickable earmarks/badges.
  - [ ] Add tag-based filtering to the Web Hub (filter posts by one or more interest groups).
- [ ] **Sponsor Filtering**
  - [ ] Add sponsor-based filtering to the Web Hub (filter posts by one or more sponsors).
  - [ ] Support combined filtering: by sponsor AND/OR interest group tags simultaneously.
- [ ] **YouTube Integration**
  - [ ] Include interest group tags on the YouTube thumbnail overlay.
  - [ ] Add interest group tags to the YouTube description and tags metadata.

## Phase 7: X/Twitter Auto-Posting & Cross-Promotion
- [ ] **X Developer API Setup**
  - [ ] Create X Developer account with Elevated access for posting.
  - [ ] Add `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET` to GitHub Secrets.
- [ ] **Gemini API Quotas & Best Practices**
  **IMPORTANT: The new `google-genai` SDK exposes the Free Tier rate limits strictly.**
  During live testing on March 16, 2026, we confirmed that Free Tier API keys trigger a hard `limit: 0` error on older models like `gemini-2.0-flash`, and hit a hard 20 Requests Per Day limit on the newest `gemini-2.5-flash` model.

  **Multi-Key Cycling (400+ Requests/Day):**
  The `engine.py` script has been upgraded to accept a comma-separated list of multiple API keys in the `.env` file (e.g., `GEMINI_API_KEY="key1,key2,key3"`). When one key hits its 20-request limit, the engine automatically rotates to the next key without failing. 

  **CRITICAL MULTI-KEY RULE:** 
  Google enforces the 20-request limit *per Google Cloud Project*, not per key string. If you generate 20 keys from the exact same Google Cloud Project, they will instantly share the same 20-request limit. 
  To successfully get 400 requests per day, you **MUST** create 20 completely separate Google Cloud Projects in the developer console, and generate 1 API key from each project.

  If the script exhausts all provided keys, it will throw a `CRITICAL: ALL provided API keys have exhausted their daily quotas!` error in the GitHub Actions terminal logs.
- [ ] **Auto-Post Pipeline**
  - [ ] After YouTube video is live and blog post is published, auto-generate an X/Twitter post.
  - [ ] Post the **raw video natively to X** (not just a YouTube link) for maximum reach and monetization.
  - [ ] Include a reply to the native post with the YouTube link for cross-promotion.
  - [ ] Use `tweepy` or X API v2 directly for automated posting.
- [ ] **Duplicate Prevention System**
  - [ ] Track which bills have been posted to YouTube and X, similar to `known_bill_ids.json`.
  - [ ] Prevent re-posting videos or tweets for bills that have already been published.

## Phase 8: CMS Management Integration
- [ ] Implement a lightweight, web-based Content Management System (CMS) directly on the website.
- [ ] Enable manual drafting, editing, and deletion of AI-generated blog posts without requiring code or JSON manipulation.
- [ ] Ensure seamless integration with the Astro framework (evaluating Git-based Headless CMS options like Keystatic, TinaCMS, or Decap).
