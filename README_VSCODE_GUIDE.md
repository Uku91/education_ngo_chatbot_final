# HopeLearn Education Chatbot - Complete Project Guide for VS Code

## Project Structure
education_ngo_chatbot/
- ngo_knowledge.txt (Knowledge base)
- app.py (Backend API)
- sheets_integration.py (Google Sheets lead capture)
- admin_dashboard.html (Admin dashboard)
- index.html (Demo website + widget)
- requirements.txt
- service_account.json (YOU ADD - from Google Cloud)
- chat_history.json (auto-created)
- leads_backup.csv (fallback if Sheets fails)

## VS CODE FULL WORKFLOW

### Step 1: Setup VS Code (10 mins)
1. Install VS Code from code.visualstudio.com
2. Install Extensions: Python (Microsoft), Live Server ( Dey)
3. Open VS Code > File > Open Folder > Select education_ngo_chatbot folder
4. Press Ctrl+` to open Terminal in VS Code

### Step 2: Create Virtual Environment
In VS Code Terminal:
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Test Knowledge Base
Open ngo_knowledge.txt, edit if needed for your NGO.

### Step 4: Run Backend
```bash
uvicorn app:app --reload --port 8000
```
You should see: Uvicorn running on http://127.0.0.1:8000
Visit http://127.0.0.1:8000/docs to test API (Swagger UI)
Visit http://127.0.0.1:8000/admin to see Admin Dashboard

### Step 5: Run Frontend Widget
- Right-click index.html > Open with Live Server (port 5500)
- Test chat bubble bottom-right. Ask: "How to volunteer?"
- The frontend currently uses keyword logic. It will work without backend.
- To connect to real backend: Open index.html, find function getAnswer(), uncomment the fetch version and set YOUR_BACKEND_URL to http://127.0.0.1:8000

### Step 6: Setup Google Sheets Lead Capture (20 mins)
1. Go to console.cloud.google.com
2. New Project: HopeEducation Bot
3. Enable APIs: Search "Google Sheets API" -> Enable, "Google Drive API" -> Enable
4. IAM & Admin > Service Accounts > Create Service Account > Name: hopeeducation-bot > Create and Continue > Done
5. Click service account > Keys > Add Key > Create New Key > JSON > Download. Rename to service_account.json and put in project folder.
6. Open the JSON, copy the client_email like hopeeducation-bot@...iam.gserviceaccount.com
7. Create Google Sheet: https://sheets.google.com -> New -> Title: "HopeEucation Leads"
8. Create 4 tabs (bottom): Volunteers, Donors, HelpRequests, ChatLogs
9. In each tab, add header row:
   Volunteers: Timestamp | Name | Phone | Email | Skill | Availability | Status
   Donors: Timestamp | Name | Phone | Email | Type | Amount/Item | Status
   HelpRequests: Timestamp | Parent Name | Child Name | Age | Location | Phone | Need | Status
   ChatLogs: Timestamp | Question | Answer | Helpful?
10. Click Share on Sheet -> Paste service account email -> Editor access -> Send (uncheck notify)
11. Now test: In VS Code terminal, python -> from sheets_integration import log_volunteer; log_volunteer("Test","080123","test@test.com","Tutor","Weekends")

### Step 7: Connect Lead Forms to Widget
Add this to your widget JS when user says "I want to volunteer":
```javascript
// After collecting details via chat
fetch('http://127.0.0.1:8000/lead/volunteer', {
  method:'POST', headers:{'Content-Type':'application/json'},
  body: JSON.stringify({name, phone, email, skill, availability})
})
```

### Step 8: Make it Real RAG with OpenAI (Optional but for good grade)
1. Get API key from platform.openai.com
2. Create .env file: OPENAI_API_KEY=sk-...
3. In app.py replace simple_retrieval with Chroma vector search:
```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import Chroma
# embed ngo_knowledge.txt and query with similarity search
```

### Step 9: Push to GitHub & Deploy
```bash
git init
git add .
git commit -m "HopeEducation chatbot complete"
# Create repo on github.com then:
git remote add origin YOUR_REPO_URL
git push -u origin main
```
Deploy backend to Render.com (Free): New Web Service > Connect GitHub > Build: pip install -r requirements.txt > Start: uvicorn app:app --host 0.0.0.0 --port 10000

### Step 10: Record Demo for Tutor
Record 2-min video: Show website, ask 3 questions, show lead appears in Google Sheet, show admin dashboard.

You are DONE!
