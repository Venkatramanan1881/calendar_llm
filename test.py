# ================================
# 📦 Imports
# ================================

# pip install streamlit pandas google-auth google-auth-oauthlib google-api-python-client pydantic langchain langchain-google-genai

import os
import pickle
import streamlit as st
import pandas as pd
from typing import Optional
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pydantic import BaseModel

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

# ================================
# 🔐 Google Auth & API Services
# ================================
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.pickle'
GEMINI_API_KEY = "AIzaSyBA0FSAKYF_OZWP6NhNDLzk4QaDCPCGZ9M"  # Replace with your actual API key

def authenticate_user():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def build_drive_service(creds):
    return build('drive', 'v3', credentials=creds)

def build_sheets_service(creds):
    return build('sheets', 'v4', credentials=creds)

# ================================
# 📊 Google Sheets Reader
# ================================
def read_sheet_data(sheet_service, spreadsheet_id: str, sheet_name: str):
    range_name = f"{sheet_name}!A1:Z1000"
    result = sheet_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get('values', [])
    if not values or len(values) < 2:
        return []
    df = pd.DataFrame(values[1:], columns=values[0])
    return df.to_dict(orient="records")

# ================================
# 🤖 Gemini + LangChain Integration
# ================================
class InvoiceQueryResponse(BaseModel):
    answer: str
    notes: Optional[str] = ""

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=GEMINI_API_KEY
    )

def ask_question_about_invoices(invoice_data: list[dict], user_question: str) -> InvoiceQueryResponse:
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=InvoiceQueryResponse)


    prompt = PromptTemplate.from_template("""
You are an assistant that helps analyze invoice data.

Here is the invoice data:
{data}

Question:
{question}

Respond in the following JSON format:
{format_instructions}
""")

    chain = (
        {
            "data": lambda x: x["data"],
            "question": lambda x: x["question"],
            "format_instructions": lambda _: parser.get_format_instructions()
        }
        | prompt
        | llm
        | parser
    )

    return chain.invoke({"data": invoice_data, "question": user_question})

# ================================
# 🚀 Streamlit UI
# ================================
def main():
    st.title("📊 Ask Questions About Invoices (Gemini 2.0 Flash)")

    creds = None
    if st.button("🔐 Authenticate"):
        creds = authenticate_user()
        st.session_state["sheets_service"] = build_sheets_service(creds)
        st.success("✅ Authenticated & connected to Google Sheets")

    if "sheets_service" in st.session_state:
        spreadsheet_id = st.text_input("Google Spreadsheet ID", "1slKRWH612u43PZ5pJo99sVW7dxDSE01Y6jLl3KwsY9E")
        sheet_name = st.text_input("Sheet Name", "InvoiceSheet")
        user_question = st.text_input("🧠 Ask your question (e.g., How many invoices today?)")

        if st.button("🔍 Ask Gemini"):
            data = read_sheet_data(st.session_state["sheets_service"], spreadsheet_id, sheet_name)
            if not data:
                st.warning("No data found in the selected sheet.")
            else:
                response = ask_question_about_invoices(data, user_question)
                st.markdown(f"### 💡 Gemini’s Answer:\n\n{response.answer}")
                if response.notes:
                    st.caption(f"💬 Notes: {response.notes}")

if __name__ == "__main__":
    main()
