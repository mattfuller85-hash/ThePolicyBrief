"""
The Policy Brief - Core Logic Engine (V7 Investigative Auditor)
Phase 3 Architect: Modular classes for strict financial auditing, sponsor doxing, and verification.
"""

import os
import json
from enum import Enum
from typing import Dict, Any, List, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
import resend
# from PIL import Image, ImageDraw, ImageFont
# import google.generativeai as genai
# import resend

LEGAL_DISCLAIMER = (
    "DISCLAIMER: The Policy Brief, LLC provides this analysis for informational "
    "and transparency purposes only. This report does not constitute legal, "
    "financial, or formal political advice. All data is sourced from public "
    "government records via automated retrieval."
)

ANCHORS = [
    {
        "name": "Marcus 'The Hawk' Hayes",
        "vibe": "The cynical, high-energy financial watchdog. Talks fast, uses banking/Wall Street analogies, has zero patience for government waste."
    },
    {
        "name": "Elena Rostova",
        "vibe": "The sharp, no-nonsense investigative reporter. Precise, slightly sarcastic, focuses on who sponsored the bill and who is making money off of it."
    },
    {
        "name": "David 'The Professor' Sterling",
        "vibe": "The calm, historical contextualizer. Speaks like an Ivy League professor deeply disappointed in his students (Congress). Focuses on bizarre spending compared to normal budgets."
    },
    {
        "name": "Chloe Kim",
        "vibe": "The Gen-Z/Millennial political outsider. Highly relatable, uses modern pacing, treats bills like ridiculous pop-culture drama."
    },
    {
        "name": "Jack Vance",
        "vibe": "The classic, booming-voice traditional News Anchor. Formal, occasionally breaks character to express utter disbelief at a pork item."
    },
    {
        "name": "Sarah 'The Auditor' Jenkins",
        "vibe": "The meticulous accountant. Cold, calculating, laser-focused on the 'pork-to-value' ratio. Loves numbers and bottom lines."
    }
]

V7_SCHEMA = """
{
  "bill_id": "String",
  "date_proposed": "String (YYYY-MM-DD)",
  "historical_context": "String (Brief context on why the bill was introduced)",
  "total_spending": "Number",
  "legitimate_spending": "Number",
  "pork_barrel_spending": "Number",
  "pork_to_value_ratio": "Number (Percentage of total spending designated as pork)",
  "fluff_detected": "Boolean",
  "fluff_items": [
    "String (Exact quote from the bill text describing the unrelated rider or earmark, e.g., the 'Coy fish pond' test)"
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
  "heygen_short_script": "String (30s-2m script. MANDATORY OPENING: You MUST start the script with EXACTLY this structure, filling in the brackets: 'Bill [Insert Bill ID here], otherwise known as the \"[Insert Bill Title here]\" that is coming to the floor for vote soon...'. Discuss any fluff/pork, and CRITICALLY: you MUST quote the exact text from the bill that contains the pork. Explicitly state who the winners and losers are at the end. IMPORTANT: Maintain a highly professional tone. Do NOT use the filler word 'like' (valleygirl style) regardless of your persona. Be engaging, but professional.)",
  "blog_post_markdown": "String (A comprehensive, authoritative blog post detailing the bill, its legitimate spending, the pork discovered, and why taxpayers should care. Use the Neutral Auditor brand voice. CRITICALLY: you MUST quote the exact text from the bill when detailing the pork discovered.)",
  "youtube_metadata": {
    "title": "String (Catchy, engaging YouTube title under 70 characters)",
    "description": "String (Detailed but punchy description of the video, including a brief summary of the bill and asking viewers for their thoughts)",
    "tags": ["String", "String", "String"],
    "thumbnail_url": "String",
    "copyright": "String"
  }
}
"""

class BrandingMode(Enum):
    PORK_ALERT = "PORK_ALERT"  # Red/Yellow
    BILL_BRIEF = "BILL_BRIEF"  # Blue/Gold

class CongressSource:
    """Handles fetching daily bills from Congress.gov API v3."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.congress.gov/v3"

    def fetch_daily_bills(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch bills recently introduced or updated from the current Congress."""
        print(f"Fetching {limit} recent bills from Congress.gov...")
        url = f"{self.base_url}/bill/119?api_key={self.api_key}&limit={limit}&sort=updateDate+desc"
        
        try:
            import requests
            response = requests.get(url)
            response.raise_for_status()
            
            data = response.json()
            return data.get("bills", [])
            
        except Exception as e:
            print(f"❌ Error fetching from Congress API: {e}")
            return []

    def fetch_bill_summary(self, congress: int, bill_type: str, bill_number: int) -> Optional[str]:
        """Fetch the summary text for a specific bill. Returns summary text or None."""
        url = (
            f"{self.base_url}/bill/{congress}/{bill_type.lower()}/{bill_number}"
            f"/summaries?api_key={self.api_key}"
        )
        try:
            import requests
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            summaries = data.get("summaries", [])
            if summaries:
                # Return the most recent summary text (strip HTML tags)
                import re
                raw = summaries[-1].get("text", "")
                return re.sub(r"<[^>]+>", "", raw).strip()
            return None
        except Exception as e:
            print(f"❌ Error fetching bill summary: {e}")
            return None

    def get_bill_id(self, bill: Dict[str, Any]) -> str:
        """Generate a unique bill ID string from a Congress API bill object."""
        return f"{bill.get('type', 'UNK')}{bill.get('number', 0)}"

class FinancialAuditor:
    """The Investigative Radar: V7 Standard for zero-hallucination financial auditing."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        try:
            from google import genai
            from google.genai import types
            self.client = genai.Client(api_key=self.api_key)
            self.types = types
        except ImportError:
            print("❌ google-genai is not installed. Please run `pip install google-genai`.")
            self.client = None
            self.types = None

    def _call_gemini_with_backoff(self, prompt: str, config: Any, max_retries: int = 4) -> Any:
        import time
        import re
        
        # Proactively pace out every single Gemini API request by 15 seconds to ensure
        # we strictly stay under the 15 RPM free-tier limit. (15s = 4 requests per minute).
        print("⏳ Pacing API: Waiting 15s to guarantee we stay under free-tier AI rate limits...")
        time.sleep(15)
        
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=prompt,
                    config=config,
                )
                return response
            except Exception as e:
                error_str = str(e)
                if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                    wait_time = 30.0 # Default wait
                    match = re.search(r'retry in ([\d\.]+)s', error_str)
                    if match:
                        wait_time = float(match.group(1)) + 2.0 # Add 2 second buffer
                    
                    # Add exponential backoff multiplier (1x, 1.5x, 2x)
                    multiplier = 1.0 + (attempt * 0.5) 
                    actual_wait = wait_time * multiplier
                    
                    if attempt < max_retries - 1:
                        print(f"⚠️ API Rate Limit Hit! Sleeping for {actual_wait:.1f}s before retry {attempt+1}/{max_retries}...")
                        time.sleep(actual_wait)
                        continue
                raise e

    def audit_bill(self, bill_text: str, bill_title: str, anchor: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Executes the Chain-of-Verification (CoVe) Two-Pass System.
        """
        if not self.client:
            return {}
            
        print("Executing CoVe Pass 1: Extraction...")
        draft_data = self._pass_1_extraction(bill_text, bill_title, anchor)
        
        if not draft_data:
            return {}
            
        print("Executing CoVe Pass 2: The Prosecutor (Verification)...")
        verified_data = self._pass_2_verification(bill_text, draft_data)
        
        return verified_data

    def generate_daily_summary_script(self, audits: List[Dict[str, Any]]) -> tuple[Dict[str, Any], str]:
        """
        Takes all audited bills for the day and generates a unified 7-10 minute 
        YouTube script summarizing them. Returns a tuple (summary_data, anchor_name)
        """
        if not self.client or not audits:
            return {}, "None"
            
        import random
        import re
        anchor = random.choice(ANCHORS)
        
        # Remove the nickname (e.g., 'The Hawk') from the anchor name for the intro
        clean_anchor_name = re.sub(r" '.*?' ", " ", anchor['name']).strip()
        
        print(f"Generating Daily Summary Long-Form Script (7-10m) with Anchor: {anchor['name']}...")
        
        # Build context from audits
        context = ""
        for i, audit in enumerate(audits):
            context += f"--- BILL {i+1}: {audit.get('bill_id')} ---\n"
            context += f"Total Spending: ${audit.get('total_spending', 0):,}\n"
            context += f"Pork Spending: ${audit.get('pork_barrel_spending', 0):,}\n"
            context += f"Context: {audit.get('historical_context', 'N/A')}\n"
            context += f"Fluff Items: {', '.join(audit.get('fluff_items', []))}\n\n"
            
        prompt = f"""
        You are writing a 7-10 minute YouTube script for "The Policy Brief".
        This is a daily recap show that breaks down today's newly proposed congressional bills.
        
        YOUR PERSONA: 
        You are {anchor['name']}. Vibe: {anchor['vibe']}
        You MUST act entirely in character. NO AI SLOP. Do NOT sound robotic or use repetitive phrasing. 
        Add a joke or human-like transition occasionally so it sounds like a real person talking to actual people.
        
        CRITICAL RULES:
        1. Do NOT just regurgitate the individual shorts; weave all these bills together into a cohesive, unique broadcast.
        2. Give a summary of all of them together, highlighting the biggest themes, the worst pork, and the overall winners and losers of the day.
        3. CRITICALLY: Whenever you mention or discuss "pork" or "fluff" from a bill, you MUST quote the exact text from the bill that describes that pork.
        
        MANDATORY INTRO: You MUST start the script exactly like this (filling in the bill names):
        "Hello, I'm {clean_anchor_name} with The Policy Brief, welcome. Today's bills are [Bill 1], [Bill 2], etc."
        
        Use the following extracted financial audits from today's bills to inform the script:
        {context}
        
        Write the complete, highly engaging 7-10 minute script. 
        Do not use markdown formatting like asterisks or bolding in the spoken text, just write it exactly as it should be read on a teleprompter.
        
        CRITICALLY: You must return the output as a strict JSON object with exactly this schema:
        {{
          "title": "String (Catchy YouTube title)",
          "description": "String (YouTube description)",
          "tags": ["String", "String"],
          "script_body": "String (The full 7-10 minute script)"
        }}
        """
        try:
            response = self._call_gemini_with_backoff(
                prompt=prompt,
                config=self.types.GenerateContentConfig(
                    temperature=0.4,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text.strip()), anchor['name']
        except Exception as e:
            print(f"❌ Gemini API Error in Summary Script: {e}")
            return {}, "None"

    def _pass_1_extraction(self, bill_text: str, bill_title: str, anchor: Dict[str, str] = None) -> Dict[str, Any]:
        """
        First pass: Extracts all dollar amounts, identifies recipients, classifies as Legitimate/Pork,
        and identifies 'Fluff' (unrelated riders/earmarks like the 'Coy fish pond' test).
        """
        
        anchor_instruction = ""
        if anchor:
            anchor_instruction = f"""
        For the `heygen_short_script`, your required PERSONA is: {anchor['name']} - {anchor['vibe']}.
        DO NOT say "Hello I am your neutral auditor" or use AI phrases. Start immediately with the bill name. 
        Act exactly like your persona. Give a brief summary, discuss any fluff/pork, and state who the winners and losers are.
            """
        else:
            anchor_instruction = """
        For the `heygen_short_script`, DO NOT say "Hello I am your neutral auditor" or use repetitive AI phrases. 
        Start immediately with the bill name. Act like a professional news anchor at a desk. Give a brief summary, 
        discuss any fluff/pork, and state who the winners and losers are. Be creative, engaging, and human-like.
            """

        prompt = f"""
        You are a highly analytical auditor AND an engaging YouTube scriptwriter. Review the following congressional bill text.
        Bill Title: {bill_title}
        
        Perform a financial audit. Extract every single dollar amount mentioned.
        Classify spending directly related to the title as 'Legitimate'.
        Classify any spending unrelated to the core purpose as 'Pork-Barrel'.
        Identify any 'Fluff' (unrelated riders or earmarks).
        
        {anchor_instruction}
        
        Ensure the final output matches EXACTLY this JSON schema:
        {V7_SCHEMA}
        
        Bill Text:
        {bill_text}
        """
        
        try:
            # V7 Standards: Strict determinism and strictly structured JSON response
            response = self._call_gemini_with_backoff(
                prompt=prompt,
                config=self.types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"❌ Gemini API Error in Pass 1: {e}")
            return {}

    def _pass_2_verification(self, source_text: str, draft_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Second pass: Acts as a 'Prosecutor'. Must verify every claim in draft_data against the source_text.
        If a claim or financial figure is NOT explicitly in the source text, it is DELETED.
        """
        prompt = f"""
        You are a Prosecutor Auditor. Your job is to verify the following drafted JSON data against the 
        source bill text. Ensure strictly zero hallucinations. If a dollar amount or claim in the draft 
        data is not explicitly present in the source text, remove it or set it to 0/False.
        
        Ensure the final output matches exactly the requested V7 schema:
        {V7_SCHEMA}
        
        Draft Data:
        {json.dumps(draft_data, indent=2)}
        
        Source Bill Text:
        {source_text}
        """
        try:
            response = self._call_gemini_with_backoff(
                prompt=prompt,
                config=self.types.GenerateContentConfig(
                    temperature=0.0,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"❌ Gemini API Error in Pass 2: {e}")
            return draft_data

    def dox_sponsor(self, sponsor_name: str) -> Dict[str, Any]:
        """Use Google Search grounding to retrieve current Phone, Website, and Social handles."""
        print(f"Retrieving contact info (Sponsor Dox) with Grounding for {sponsor_name}...")
        prompt = f"""
        Find the current official Washington DC phone number, official website, and any 
        official social media handles (Twitter/X, Facebook, Instagram) for US Senator/Representative {sponsor_name}.
        Respond in strict JSON with these keys: 
        "sponsor_name", "phone_number", "website", "social_handles" (an object with "twitter", "facebook", "instagram" keys).
        """
        try:
            response = self._call_gemini_with_backoff(
                prompt=prompt,
                config=self.types.GenerateContentConfig(
                    temperature=0.0,
                    tools=[{"google_search": {}}],
                ),
            )
            # Search grounding sometimes returns markdown code blocks
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            elif text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
                
            return json.loads(text.strip())
        except Exception as e:
            print(f"❌ Gemini API Error in Sponsor Dox: {e}")
            return {
                "sponsor_name": sponsor_name,
                "phone_number": "Unknown",
                "website": "Unknown",
                "social_handles": {}
            }

class ThumbnailGenerator:
    """The Content Factory: Adaptive Thumbnail & Blog Image Engine."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_thematic_visual(self, prompt: str) -> str:
        """Use Imagen/Gemini to generate a high-quality thematic visual for the right side."""
        print(f"Generating image with AI for prompt: {prompt}")
        return "/tmp/thematic_base.png"

    def composite_thumbnail(self, base_image_path: str, bill_id: str, fluff_detected: bool) -> str:
        """
        Apply the "Master Template" (70/30 split).
        IF fluff_detected: Red/Yellow ("PORK ALERT"). ELSE: Blue/Gold ("BILL BRIEF").
        """
        branding = BrandingMode.PORK_ALERT if fluff_detected else BrandingMode.BILL_BRIEF
        print(f"Compositing thumbnail. Branding: {branding.value}")
        return f"/tmp/thumbnail_{bill_id}.png"

class ResendDelivery:
    """The Digital Desktop: Immediate HTML email delivery for scripts."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        resend.api_key = api_key

    def deliver_short_script(self, audit: Dict[str, Any], to_email: str) -> bool:
        """Emails a single generated short script instantly."""
        if not self.api_key:
            print("❌ Resend API key missing. Cannot deliver script.")
            return False
            
        print(f"📧 Sending Short script email for {audit.get('bill_id')}...")
        
        a_name = audit.get('anchor_name', 'Unknown Anchor')
        meta = audit.get('youtube_metadata', {})
        title = meta.get('title', 'Untitled')
        
        html_content = f"""
        <h2>🚨 New Policy Brief Script Ready!</h2>
        <p><strong>Bill:</strong> {audit.get('bill_id')}</p>
        <p><strong>Assigned Anchor:</strong> {a_name}</p>
        <hr>
        <h3>YouTube Metadata</h3>
        <p><strong>Title:</strong> {title}</p>
        <p><strong>Description:</strong> {meta.get('description', 'No description generated.')}</p>
        <p><strong>Tags:</strong> {', '.join(meta.get('tags', []))}</p>
        <hr>
        <h3>HeyGen Script (30s-2m)</h3>
        <pre style="font-family: Arial, sans-serif; white-space: pre-wrap;">
        {audit.get('heygen_short_script', 'No script generated.')}
        </pre>
        """
        
        try:
            r = resend.Emails.send({
                "from": "The Policy Brief <onboarding@resend.dev>",
                "to": to_email,
                "subject": f"New Script: {audit.get('bill_id')} - {title}",
                "html": html_content
            })
            print(f"✅ Delivered Short Script to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Resend API Error (Short): {e}")
            return False

    def deliver_daily_summary(self, summary_data: Dict[str, Any], anchor: str, to_email: str) -> bool:
        """Emails the end-of-day long-form master summary script."""
        if not self.api_key:
            return False
            
        print(f"📧 Sending Nightly Summary script email...")
        
        html_content = f"""
        <h2>📺 Nightly Summary Script Ready!</h2>
        <p><strong>Assigned Anchor:</strong> {anchor}</p>
        <hr>
        <h3>YouTube Metadata</h3>
        <p><strong>Title:</strong> {summary_data.get('title', 'Untitled Summary')}</p>
        <p><strong>Description:</strong> {summary_data.get('description', 'No description.')}</p>
        <p><strong>Tags:</strong> {', '.join(summary_data.get('tags', []))}</p>
        <hr>
        <h3>HeyGen Master Script (7-10m)</h3>
        <pre style="font-family: Arial, sans-serif; white-space: pre-wrap;">
        {summary_data.get('script_body', summary_data.get('script', 'No script generated.'))}
        </pre>
        <hr>
        <p>{LEGAL_DISCLAIMER}</p>
        """
        
        try:
            r = resend.Emails.send({
                "from": "The Policy Brief <onboarding@resend.dev>",
                "to": to_email,
                "subject": f"Nightly Summary: {summary_data.get('title', 'Policy Brief')}",
                "html": html_content
            })
            print(f"✅ Delivered Nightly Summary to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Resend API Error (Summary): {e}")
            return False

class ResendMessenger:
    """The Weekly Briefing: Friday newsletter delivery."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        resend.api_key = api_key

    def generate_weekly_wall_of_shame(self, weekly_audits: List[Dict[str, Any]]) -> str:
        """
        Sorts the week's audits by pork-to-value ratio and generates an HTML newsletter
        highlighting the top 5 worst offenders (The Value Audit).
        """
        # Filter for bills that actually had fluff detected and have a valid ratio
        fluff_bills = [b for b in weekly_audits if b.get('fluff_detected') and isinstance(b.get('pork_to_value_ratio'), (int, float))]
        
        # Sort descending by pork ratio
        fluff_bills.sort(key=lambda x: x.get('pork_to_value_ratio', 0), reverse=True)
        
        # Take top 5
        top_5 = fluff_bills[:5]
        
        total_pork = sum(b.get('pork_barrel_spending', 0) for b in weekly_audits if isinstance(b.get('pork_barrel_spending'), (int, float)))
        
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #1a1a1a; color: #ffffff; padding: 20px;">
            <div style="text-align: center; border-bottom: 2px solid #ff4444; padding-bottom: 20px; margin-bottom: 20px;">
                <h1 style="color: #ff4444; margin: 0; text-transform: uppercase;">The Policy Brief</h1>
                <h2 style="color: #aaaaaa; margin: 5px 0 0 0;">The Weekly Value Audit</h2>
            </div>
            
            <div style="background-color: #2a2a2a; border-left: 4px solid #ffaa00; padding: 15px; margin-bottom: 30px;">
                <h3 style="margin-top: 0; color: #ffaa00;">Weekly Damage Report</h3>
                <p style="font-size: 18px; margin: 0;">Total Pork Identified This Week: <strong>${total_pork:,.2f}</strong></p>
            </div>
            
            <p style="font-size: 16px; line-height: 1.5;">Welcome to the Friday Briefing. Here are the top {len(top_5)} most egregious examples of wasteful spending we caught on the radar this week.</p>
        """
        
        for i, bill in enumerate(top_5, 1):
            ratio = bill.get('pork_to_value_ratio', 0)
            pork_amt = bill.get('pork_barrel_spending', 0)
            title = bill.get('title', 'Unknown Title')
            bill_id = bill.get('bill_id', 'Unknown ID')
            sponsor = bill.get('sponsor_contact_info', {})
            s_name = sponsor.get('sponsor_name', 'Unknown Sponsor')
            s_phone = sponsor.get('phone_number', 'No phone available')
            
            fluff_items = bill.get('fluff_items', [])
            fluff_bullets = "".join([f"<li style='margin-bottom: 5px;'>{item}</li>" for item in fluff_items])
            
            html += f"""
            <div style="background-color: #222222; border: 1px solid #333333; padding: 20px; margin-bottom: 20px; border-radius: 5px;">
                <h3 style="margin-top: 0; color: #ff5555; border-bottom: 1px solid #444; padding-bottom: 10px;">#{i} - {bill_id}</h3>
                <h4 style="margin-top: 10px; color: #ffffff;">{title}</h4>
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <span style="background-color: #331111; color: #ff6666; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{ratio:.1f}% Pork</span>
                    <span style="background-color: #113311; color: #66ff66; padding: 5px 10px; border-radius: 3px; font-weight: bold;">Waste: ${pork_amt:,.2f}</span>
                </div>
                
                <h5 style="color: #aaaaaa; margin-bottom: 5px;">Text from the Bill:</h5>
                <ul style="color: #cccccc; padding-left: 20px; font-style: italic; margin-top: 0;">
                    {fluff_bullets}
                </ul>
                
                <div style="margin-top: 15px; padding-top: 15px; border-top: 1px dashed #444;">
                    <h5 style="color: #aaaaaa; margin: 0 0 5px 0;">Hold Them Accountable:</h5>
                    <p style="margin: 0; color: #ffffff;"><strong>Sponsor:</strong> {s_name}</p>
                    <p style="margin: 0; color: #ffffff;"><strong>Phone:</strong> <a href="tel:{s_phone}" style="color: #4da6ff;">{s_phone}</a></p>
                </div>
            </div>
            """
            
        html += f"""
            <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #444; color: #888888; font-size: 12px;">
                <p>{LEGAL_DISCLAIMER}</p>
                <p>&copy; 2026 The Policy Brief. All rights reserved.</p>
            </div>
        </div>
        """
        return html

    def send_weekly_briefing(self, weekly_audits: List[Dict[str, Any]], to_email: str) -> bool:
        """Generates and emails the Friday newsletter."""
        if not self.api_key:
            print("❌ Resend API key missing. Cannot deliver newsletter.")
            return False
            
        print(f"📧 Formatting and sending The Weekly Value Audit...")
        html_content = self.generate_weekly_wall_of_shame(weekly_audits)
        
        try:
            params: resend.Emails.SendParams = {
                "from": "The Policy Brief <onboarding@resend.dev>",
                "to": [to_email],
                "subject": "🚨 The Weekly Value Audit: Top 5 Pork Bills",
                "html": html_content,
            }
            r = resend.Emails.send(params)
            print(f"✅ Delivered Weekly Newsletter to {to_email}")
            return True
        except Exception as e:
            print(f"❌ Resend API Error (Newsletter): {e}")
            return False


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    print("The Policy Brief Engine Loaded (V7 Auditor Standards).")
    
    congress_key = os.getenv("CONGRESS_API_KEY")
    if congress_key:
        print("\n--- Testing Congress API ---")
        source = CongressSource(api_key=congress_key)
        recent_bills = source.fetch_daily_bills(limit=1)
        for i, bill in enumerate(recent_bills):
            print(f"[{i+1}] {bill.get('type')} {bill.get('number')} - {bill.get('title')}")
    else:
        print("⚠️ CONGRESS_API_KEY not found. Skipping Congress API test.")

    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print("\n--- Testing Financial Auditor (V7 CoVe Pipeline) ---")
        auditor = FinancialAuditor(api_key=gemini_key)
        
        # Test Sponsor Dox (Search Grounding)
        sponsor_data = auditor.dox_sponsor("Senator Elizabeth Warren")
        print("\nSponsor Dox Result:")
        print(json.dumps(sponsor_data, indent=2))
        
        # Test CoVe Pipeline with Mock Bill
        mock_bill_title = "The Community Bridge and Coy Fish Pond Act of 2024"
        mock_bill_text = "This bill allocates $30,000,000 for the construction of a new suspension bridge connecting the two main commercial districts. Additionally, a rider has been attached to allocate $5,000,000 for a luxury coy fish pond in the mayor's backyard, completely unrelated to the bridge infrastructure."
        
        print("\nExecuting CoVe Pipeline...")
        audit_result = auditor.audit_bill(mock_bill_text, mock_bill_title)
        print("\n--- FINAL VERIFIED AUDIT ---")
        print(json.dumps(audit_result, indent=2))
    else:
        print("⚠️ GEMINI_API_KEY not found. Skipping Financial Auditor test.")
