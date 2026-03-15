# The Policy Brief - API Setup & Acquisition Guide

This guide outlines exactly how to obtain the necessary API keys for the core infrastructure of "The Policy Brief."

---

## 🏛️ 1. Congress.gov API (The Baseline Text)
*Purpose: Fetches the raw daily bill text, fundamental metadata, and official actions.*
1. Go to: [api.congress.gov/sign-up](https://api.congress.gov/sign-up/)
2. Fill out your First Name, Last Name, and Email.
3. Accept the Terms of Service and click **Sign Up**.
4. The API Key (`CONGRESS_API_KEY`) will be displayed on the screen immediately and emailed to you.

---

## 📰 [DEPRECATED] 2. ProPublica Congress API
*Note: The ProPublica Congress API is no longer available to new users. We will rely on Congress.gov and GovTrack for voting data and sponsor metadata.*

## 💰 [UPDATED] 3. Federal Election Commission (FEC) API (The Money Trail)
*Purpose: Replaces OpenSecrets. Uncovers campaign finance data, PAC funding, and contributor information to find the real incentives behind the fluff.*
1. Go to: [api.data.gov/signup/](https://api.data.gov/signup/)
2. Fill out your First Name, Last Name, and Email.
3. Your API key will be displayed immediately and sent to your email.
4. Note: You can use the exact same key for both the Congress.gov API and the FEC API, as they are both hosted by Data.gov! You can just copy your `CONGRESS_API_KEY` into the `FEC_API_KEY` slot.

---

## 🧠 4. Gemini API (The Financial Auditor)
*Purpose: Parses thousands of pages of legalese in seconds to itemize costs, detect fluff, and write the newsletter scripts.*
1. Go to Google AI Studio: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account.
3. Click the **"Create API Key"** button (top left).
4. Select a Google Cloud Project (or create a new one, e.g., "Policy Brief Auditor").
5. Copy the generated API Key (`GEMINI_API_KEY`).

---

## 📺 5. YouTube API (The Content Factory)
*Purpose: (Optional for Phase 1, required for automated video uploading).*
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (e.g., "Policy Brief YouTube").
3. Navigate to **APIs & Services > Library**.
4. Search for **"YouTube Data API v3"** and click **Enable**.
5. Go to **APIs & Services > Credentials**.
6. Click **Create Credentials > API Key**.
7. Save your key (`YOUTUBE_API_KEY`).

---

## 📧 6. Resend API (The Weekly Briefing)
*Purpose: Sending the automated HTML Friday Newsletter.*
1. Go to: [resend.com](https://resend.com/)
2. Sign up for an account (the free tier allows 3,000 emails/month).
3. Navigate to the **API Keys** tab on the left sidebar.
4. Click **Create API Key**. Give it full access (or sending access).
5. Copy the key immediately (it only shows once) and save it as `RESEND_API_KEY`.

---

## 📄 7. Google Drive API (The Digital Desktop)
*Purpose: (Hardest to set up) Allows Python to auto-generate the daily Google Doc with your scripts.*
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Select your project.
3. Go to **APIs & Services > Library**, search for **"Google Docs API"** and **"Google Drive API"**, and Enable both.
4. Go to **Credentials**, click **Create Credentials > Service Account**.
5. Name it (e.g., "Policy Brief Bot") and click Create.
6. Click on the new Service Account, go to the **Keys** tab, and click **Add Key > Create new key > JSON**.
7. The JSON file will download to your computer.
8. Set the path to this file as `GOOGLE_DRIVE_CREDENTIALS` in your `.env`.
9. *Crucial Step*: Open the JSON, find the `"client_email"`, and "Share" your target Google Drive folder with that exact email address.
