
# sheets_integration.py - Capture Volunteer/Donor leads to Google Sheets
# How to setup Google Sheets API (Free):
# 1. Go to console.cloud.google.com -> Create Project -> Enable Google Sheets API & Google Drive API
# 2. Create Service Account -> Create Key (JSON) -> Download as service_account.json
# 3. Create a Google Sheet named "HopeEducation Leads" with tabs: Volunteers, Donors, HelpRequests, ChatLogs
# 4. Share the sheet with the service_account email (from JSON) as Editor

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

SHEET_NAME = "HopeEducation Leads"
CREDENTIALS_FILE = "service_account.json"  # Place in same folder

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    return client.open(SHEET_NAME)

def log_volunteer(name, phone, email, skill, availability):
    try:
        sh = get_sheet()
        ws = sh.worksheet("Volunteers")
        ws.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), name, phone, email, skill, availability, "New"])
        return True
    except Exception as e:
        print(f"Sheets error: {e} - logging locally instead")
        with open("leads_backup.csv","a") as f:
            f.write(f"{datetime.now()},VOLUNTEER,{name},{phone},{email},{skill},{availability}\n")
        return False

def log_donor(name, phone, email, donation_type, amount_or_item):
    try:
        sh = get_sheet()
        ws = sh.worksheet("Donors")
        ws.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), name, phone, email, donation_type, amount_or_item, "New"])
        return True
    except Exception as e:
        print(f"Sheets error: {e}")
        with open("leads_backup.csv","a") as f:
            f.write(f"{datetime.now()},DONOR,{name},{phone},{email},{donation_type},{amount_or_item}\n")
        return False

def log_help_request(parent_name, child_name, child_age, location, phone, need):
    try:
        sh = get_sheet()
        ws = sh.worksheet("HelpRequests")
        ws.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), parent_name, child_name, child_age, location, phone, need, "Pending Verification"])
        return True
    except Exception as e:
        print(f"Sheets error: {e}")
        with open("leads_backup.csv","a") as f:
            f.write(f"{datetime.now()},HELP,{parent_name},{child_name},{child_age},{location},{phone},{need}\n")
        return False

def log_chat(question, answer, was_helpful=None):
    try:
        sh = get_sheet()
        ws = sh.worksheet("ChatLogs")
        ws.append_row([datetime.now().strftime("%Y-%m-%d %H:%M"), question, answer, was_helpful or ""])
    except:
        with open("chat_logs.csv","a") as f:
            f.write(f'"{datetime.now()}","{question}","{answer}"\n')
