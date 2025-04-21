# Calendar Automation

This project automates calendar and email tasks using Google Calendar and Gmail APIs.

## Files

- `calendar_auth_llm.py`: This file uses the Gemini 1.5 Flash model to schedule meetings via Google Calendar. It uses Streamlit to create a user interface for scheduling meetings.
- `gmail_calendar.py`: This file provides functions for sending emails, creating drafts, reading recent emails, and searching emails using the Gmail API.
- `credentials.json`: This file contains the credentials for authenticating with the Google Calendar and Gmail APIs.

## Requirements

- Python 3.6+
- Google API credentials (`credentials.json`)

## Setup

1.  Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

2.  Obtain Google API credentials:

    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project.
    *   Enable the Google Calendar API and Gmail API.
    *   Create a service account and download the credentials file as `credentials.json`.

## Usage

### calendar\_auth\_llm.py

1.  Run the Streamlit app:

    ```bash
    streamlit run calendar_auth_llm.py
    ```

2.  Enter a description of the meeting in the text input field.
3.  The app will schedule the meeting and display a link to the event in Google Calendar.

### gmail\_calendar.py

This file provides functions for interacting with the Gmail API. You can use these functions to send emails, create drafts, read recent emails, and search emails.

Example:

```python
from gmail_calendar import authenticate_google_services, send_email, EmailContent

# Authenticate with the Gmail API
service = authenticate_google_services()

# Create an EmailContent object
email = EmailContent(
    to="recipient@example.com",
    subject="Test Email",
    body="This is a test email sent from the Calendar Automation project."
)

# Send the email
send_email(service, email)
