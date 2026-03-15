# The Policy Brief - Research Findings

## Congress.gov API v3
- **Purpose**: Fetch daily bills to audit and official full text.
- **Requirements**: API Key needed (`CONGRESS_API_KEY`).
- **Data Extracted**: Bill ID, Title, Committees, and the full text of the bill to pass to the Financial Auditor.

## ProPublica Congress API
- **Purpose**: Digestible bill actions, member data (social media handles), and voting records.
- **Requirements**: API Key needed (`PROPUBLICA_API_KEY`).
- **Data Extracted**: Sponsor details, recent actions, and structured voting data.

## OpenSecrets API
- **Purpose**: The "Follow the Money" trail.
- **Requirements**: API Key needed (`OPENSECRETS_API_KEY`).
- **Data Extracted**: Funding sources, top donor industries, and PAC contributions for primary sponsors to uncover the incentives behind the bill.

## GovTrack.us API / Bulk Data
- **Purpose**: Predictive modeling & metadata.
- **Requirements**: Free/No-auth for basic bulk endpoints.
- **Data Extracted**: Bill passing probabilities and historical metadata.

## Google Docs API
- **Purpose**: "The Digital Desktop" delivery for scripts and metadata.
- **Requirements**: Service Account credentials (`GOOGLE_DRIVE_CREDENTIALS`).
- **Usage**: `google-api-python-client` to format and insert text (HeyGen scripts, Short scripts, and YouTube metadata) into a newly generated document each morning.

## Resend API
- **Purpose**: "The Weekly Briefing" newsletter delivery.
- **Requirements**: API Key needed (`RESEND_API_KEY`).
- **Usage**: Use the `resend` Python SDK to aggregate the top 5 "Pork-Filled" bills and send out a responsive HTML newsletter every Friday.

## AI Image Generation (Imagen/Gemini)
- **Purpose**: Generate high-quality thematic visuals for the right side of the adaptive thumbnails.
- **Requirements**: API Key (`GEMINI_API_KEY`). Let Gemini or Imagen APIs handle visual generation based on the subject matter of the bill.

## Python (PIL/Pillow) - Conditional Thumbnail Engine
- **Purpose**: The "Master Template" for the Web Hub and Content Factory.
- **Logic**: Combines AI-generated thematic visuals with a consistent 70/30 split layout.
- **Conditions**:
  - `IF fluff_detected == true`: Apply high-contrast red/yellow branding and overlay the text "PORK ALERT" alongside the Bill ID.
  - `IF fluff_detected == false`: Apply neutral brand colors (blue/gold) and overlay the text "BILL BRIEF" or "LEGISLATIVE UPDATE" alongside the Bill ID.
