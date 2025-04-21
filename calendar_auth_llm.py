from google import genai
import json
import re
import os
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate

load_dotenv()
# Load environment variables from .env file
client = genai.Client(api_key="")  # Replace with your actual API key

os.environ["GOOGLE_API_KEY"] = ""



class MeetingInfo(BaseModel):
    title: str = Field(..., description="Title of the meeting")
    startTime: str = Field(..., description="Start time of the meeting in ISO 8601 format with +05:30 timezone")
    endTime: str = Field(..., description="End time of the meeting in ISO 8601 format with +05:30 timezone")
    duration_minutes: int = Field(..., description="Duration of the meeting in minutes")
    attendees: List[str] = Field(..., description="List of email addresses of attendees")

# Step 2: Create function
def langchain_llm_call(user_input: str) -> dict:
    parser = PydanticOutputParser(pydantic_object=MeetingInfo)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a smart assistant that schedules meetings and responds in structured format."),
        ("human", """Extract meeting details from the user's input and return it in the specified structure.
Make sure all times are in ISO 8601 format and the timezone is +05:30 (IST).

{format_instructions}

User input: {user_input}
""")
    ])

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    chain = prompt | llm | parser

    result = chain.invoke({
        "user_input": user_input,
        "format_instructions": parser.get_format_instructions()
    })

    return result.dict()

def authenticate_google_calendar():
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES
    )
    creds = flow.run_local_server(port=0)
    service = build('calendar', 'v3', credentials=creds)
    print(service)
    return service

def meeting_scheduler(service, meeting_info):
    try:
        event = {
            'summary': meeting_info.get('title', 'Meeting'),
            'start': {
                    "dateTime": meeting_info['startTime'],
                    "timeZone": 'Asia/Kolkata',
                      },
            'end': {
                    "dateTime": meeting_info['endTime'],
                    "timeZone": 'Asia/Kolkata',
            },
            'attendees': [{'email': email} for email in meeting_info.get('attendees', [])],
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event.get('htmlLink', 'Event scheduled but no link returned.')
    except Exception as e:
        return e

# Streamlit App Code
st.title("Meeting Scheduler Agent")
user_input = st.text_input("Say something.... ")
if user_input:
    a1 = langchain_llm_call(user_input)
    service = authenticate_google_calendar()
    a2 = meeting_scheduler(service, a1)
    st.success(a2)
    print(a2)
