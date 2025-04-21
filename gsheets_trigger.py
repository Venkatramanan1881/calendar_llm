# 1DF52IA8gCFRbRzVYivUbnrkpe2SeMPHbk6pEmuNM-Q0

# Now we can track a specific column in the Google Sheet for changes.
# This script will check for changes in Column C of the specified Google Sheet every 10 seconds.
import time
import pickle
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# Constants
SPREADSHEET_ID = '1DF52IA8gCFRbRzVYivUbnrkpe2SeMPHbk6pEmuNM-Q0'
RANGE_NAME = 'Sheet1!C1:C'  # Watching Column C
CHECK_INTERVAL = 10  # in seconds

def get_credentials():
    token_path = 'token.pickle'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            return pickle.load(token)
    else:
        raise Exception("token.pickle not found. Run the auth flow first.")

def fetch_column_values(service):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    values = result.get('values', [])
    # Flatten list (in case of empty cells)
    return [row[0] if row else '' for row in values]

def watch_column_changes():
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    print(f"🔍 Watching column C of spreadsheet `{SPREADSHEET_ID}` every {CHECK_INTERVAL}s...")

    prev_values = fetch_column_values(service)

    while True:
        time.sleep(CHECK_INTERVAL)
        current_values = fetch_column_values(service)

        max_len = max(len(prev_values), len(current_values))

        for i in range(max_len):
            prev = prev_values[i] if i < len(prev_values) else ''
            curr = current_values[i] if i < len(current_values) else ''

            if prev != curr:
                print(f"🔁 Row {i + 1} changed in Column C: '{prev}' ➜ '{curr}'")

        prev_values = current_values

if __name__ == '__main__':
    watch_column_changes()
