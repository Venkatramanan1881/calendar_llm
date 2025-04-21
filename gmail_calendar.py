from typing import List, Optional
from pydantic import BaseModel, EmailStr
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64


# ---------------- Pydantic Models ----------------

class EmailContent(BaseModel):
    to: EmailStr
    subject: str
    body: str


class EmailSnippet(BaseModel):
    subject: str
    sender: str
    snippet: str


# ---------------- Authentication ----------------

def authenticate_google_services(scopes: Optional[List[str]] = None):
    if scopes is None:
        scopes = [
            'https://www.googleapis.com/auth/calendar',
            'https://mail.google.com/',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.readonly',
        ]
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
    creds = flow.run_local_server(port=0)
    gmail_service = build('gmail', 'v1', credentials=creds)
    return gmail_service


# ---------------- Gmail Operations ----------------

def send_email(service, email: EmailContent):
    message = MIMEText(email.body)
    message['to'] = email.to
    message['subject'] = email.subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw_message}

    result = service.users().messages().send(userId='me', body=message_body).execute()
    return result


def create_draft(service, email: EmailContent):
    message = MIMEText(email.body)
    message['to'] = email.to
    message['subject'] = email.subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft_body = {'message': {'raw': raw_message}}

    result = service.users().drafts().create(userId='me', body=draft_body).execute()
    return result


def read_recent_emails(service, max_results: int = 5) -> List[EmailSnippet]:
    results = service.users().messages().list(userId='me', maxResults=max_results, labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "(Unknown Sender)")
        snippet = msg_data.get('snippet', '')
        emails.append(EmailSnippet(subject=subject, sender=sender, snippet=snippet))
    return emails


def search_emails(service, query: str, max_results: int = 5) -> List[EmailSnippet]:
    results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "(No Subject)")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "(Unknown Sender)")
        snippet = msg_data.get('snippet', '')
        emails.append(EmailSnippet(subject=subject, sender=sender, snippet=snippet))
    return emails
