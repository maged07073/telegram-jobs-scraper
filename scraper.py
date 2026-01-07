from telethon import TelegramClient
import json
import asyncio
import re
import os
import base64
from datetime import timezone

# ====== Session ======
SESSION_NAME = "telegram"

session_b64 = os.environ.get("TELEGRAM_SESSION")
if not session_b64:
    raise RuntimeError("❌ TELEGRAM_SESSION غير موجود في Secrets")

with open(f"{SESSION_NAME}.session", "wb") as f:
    f.write(base64.b64decode(session_b64))

# ====== بيانات سرية ======
api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]

# ====== القنوات ======
channels = [
    "Engineers_Jobs",
    "Platform_courses",
    "atalla3",
    "jobsjeddah24",
    "ksageometryjobs",
    "Jobs_Saudi_Engineering",
    "almusaedEng",
    "handasiah",
    "jobzaty"
]

# ====== الكلمات المفتاحية ======
keywords = [
    "مهندس", "engineer", "ميكانيكي", "ميكانيكا", "وظيفة",
    "مهندس ميكانيكي", "Mechanical Engineer", "mechanical engineer",
    "تصميم ميكانيكي", "Maintenance Engineer", "مهندس صيانة",
    "Production Engineer", "مهندس مشاريع"
]

# ====== Regex ======
email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
phone_regex = r"(?:\+966|0)?5\d{8}"
link_regex = r"(https?://[^\s]+)"

client = TelegramClient(SESSION_NAME, api_id, api_hash)

# ====== وظائف ======
def load_jobs():
    if os.path.exists("jobs.json"):
        with open("jobs.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_jobs(jobs):
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

def is_duplicate(jobs, text):
    return any(text == job["description"] for job in jobs)

# ====== الجلب ======
async def fetch_jobs():
    jobs = load_jobs()

    for channel in channels:
        try:
            entity = await client.get_input_entity(channel)
            messages = await client.get_messages(entity, limit=50)

            for msg in messages:
                text = msg.message
