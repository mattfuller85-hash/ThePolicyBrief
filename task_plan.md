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
- [ ] Dynamic Overlay: Branding changes from "Pork Alert" (Red) to "Official Brief" (Blue/Gold) based on audit findings.
- [ ] Brand Voice: Unapologetic, transparent, and objective. "The People's Money."

## Phase 5: Deploy (The "Trigger" Phase)
- [ ] Initialize Git repository and push to GitHub.
- [ ] Generate GitHub Action for the 3:00 AM Daily Run.
- [ ] Generate GitHub Action for the Friday Newsletter Blast.
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
- [ ] **Auto-Post Pipeline**
  - [ ] After YouTube video is live and blog post is published, auto-generate an X/Twitter post.
  - [ ] Post the **raw video natively to X** (not just a YouTube link) for maximum reach and monetization.
  - [ ] Include a reply to the native post with the YouTube link for cross-promotion.
  - [ ] Use `tweepy` or X API v2 directly for automated posting.
- [ ] **Duplicate Prevention System**
  - [ ] Track which bills have been posted to YouTube and X, similar to `known_bill_ids.json`.
  - [ ] Prevent re-posting videos or tweets for bills that have already been published.
