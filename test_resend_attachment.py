import os
import resend
from dotenv import load_dotenv

load_dotenv()
resend.api_key = os.getenv("RESEND_API_KEY")

thumbnail_path = "web/public/thumbnails/HRES1074_thumbnail.jpg"

try:
    email_params = {
        "from": "The Policy Brief <onboarding@resend.dev>",
        "to": "mattfuller85@gmail.com",
        "subject": "Test attachment",
        "html": "<p>test</p>"
    }
    
    if os.path.exists(thumbnail_path):
        with open(thumbnail_path, "rb") as f:
            file_data = f.read()
            
        print(f"File size: {len(file_data)} bytes")
        
        email_params["attachments"] = [
            {
                "filename": os.path.basename(thumbnail_path),
                "content": list(file_data)
            }
        ]
        
    print("Calling resend API...")
    r = resend.Emails.send(email_params)
    print("Success:", r)
except Exception as e:
    import traceback
    traceback.print_exc()
