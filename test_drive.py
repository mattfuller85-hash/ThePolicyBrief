import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()
creds_path = os.getenv("GOOGLE_DRIVE_CREDENTIALS")
folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
scopes = ['https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file(creds_path, scopes=scopes)

drive_service = build('drive', 'v3', credentials=creds)
try:
    results = drive_service.files().list(q=f"'{folder_id}' in parents", fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    print(f"✅ Found {len(items)} files in folder {folder_id}.")

    # Now try to create a file using drive API
    body = {
        'name': 'Test Drive Doc',
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }
    doc = drive_service.files().create(body=body).execute()
    print("✅ Created doc using Drive API:", doc.get('id'))
except Exception as e:
    import traceback
    traceback.print_exc()
    print("❌ Failed:", e)
