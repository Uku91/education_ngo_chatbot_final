
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import json
from datetime import datetime
from sheets_integration import log_volunteer, log_donor, log_help_request, log_chat


KNOWLEDGE_PATH = Path(__file__).parent / "ngo_knowledge.txt"

def simple_retrieval(question: str) -> str:
    text = KNOWLEDGE_PATH.read_text(encoding="utf-8")
    q_words = question.lower().split()
    relevant = []
    for para in text.split("\n\n"):
        score = sum(1 for w in q_words if w in para.lower())
        if score > 0:
            relevant.append((score, para))
    relevant.sort(reverse=True)
    top = [p for s,p in relevant[:3]]
    return "\n\n".join(top) if top else "No relevant info found."

app = FastAPI(title="HopeLearn Chatbot API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Data models
class Query(BaseModel):
    message: str
    session_id: str = "anonymous"

class VolunteerEducation(BaseModel):
    name: str
    phone: str
    email: str
    skill: str
    availability: str
 
class DonorEducation(BaseModel):
    name: str
    phone: str
    email: str
    donation_type: str # Cash, In-kind, Sponsor a Child
    amount_or_item: str

class HelpEducation(BaseModel):
    parent_name: str
    child_name: str
    child_age: str
    location: str
    phone: str
    need: str


CHAT_HISTORY_FILE = "chat_history.json"
#  function to save chat history files including questions, answers and id 
def save_chat_history(q, a, sid):
    entry = {"time": datetime.now().isoformat(), "session": sid, "q": q, "a": a}
    try:
        if Path(CHAT_HISTORY_FILE).exists():
            data = json.loads(Path(CHAT_HISTORY_FILE).read_text())
        else:
            data = []
        data.append(entry)
        Path(CHAT_HISTORY_FILE).write_text(json.dumps(data, indent=2))
    except Exception as e:
        print(e)

@app.get("/")
def root():
    return {"status": "HopeEducation Bot running", "endpoints": ["/chat", "/lead/volunteer", "/lead/donor", "/lead/help", "/admin"]}

@app.post("/chat")
def chat(q: Query):
    context = simple_retrieval(q.message)
    # Simple intent detection
    q_low = q.message.lower()
    if "volunteer" in q_low:
        answer = f"That is Great! We need volunteers. {context[:800]}\n\nTo register, please fill: Name, Phone, Skill (Tutor/Mentor/Fundraiser). Would you like me to register you now? Type your details."
    elif "donate" in q_low or "sponsor" in q_low:
        answer = f"Thank you for wanting to donate! {context[:800]}\n\nI can log your donation interest. Tell me your name and what you want to donate."
    else:
        answer = f"{context[:1000]}\n\nNeed more help? Call +234 803 123 4567 (Monday-Friday 9am-4pm)."
    
    save_chat_history(q.message, answer, q.session_id)
    log_chat(q.message, answer)
    return {"answer": answer, "source": context[:500]}

@app.post("/lead/volunteer")
def volunteer_lead(lead: VolunteerEducation):
    log_volunteer(lead.name, lead.phone, lead.email, lead.skill, lead.availability)
    save_chat_history(f"VOLUNTEER LEAD: {lead.name}", str(lead.dict()), "lead")
    return {"status": "success", "message": f"Thanks {lead.name}! Volunteer team will contact you within 24hrs on {lead.phone}."}

@app.post("/lead/donor")
def donor_lead(lead: DonorEducation):
    log_donor(lead.name, lead.phone, lead.email, lead.donation_type, lead.amount_or_item)
    return {"status": "success", "message": f"Thank you {lead.name}! Donation team will send receipt details to {lead.email}."}

@app.post("/lead/help")
def help_lead(lead: HelpEducation):
    log_help_request(lead.parent_name, lead.child_name, lead.child_age, lead.location, lead.phone, lead.need)
    return {"status": "success", "message": f"Thanks {lead.parent_name}. We logged request for {lead.child_name} in {lead.location}. Verification in 2 weeks. Keep phone on."}

@app.get("/admin")
def admin_page():
    return FileResponse("admin_dashboard.html")

@app.get("/api/history")
def get_history():
    if Path(CHAT_HISTORY_FILE).exists():
        return json.loads(Path(CHAT_HISTORY_FILE).read_text())[-100:] # last 100
    return []

# To run: uvicorn app:app --reload --port 8000
