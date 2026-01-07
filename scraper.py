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
                if not text or is_duplicate(jobs, text):
                    continue

                for key in keywords:
                    if key.lower() in text.lower():
                        job = {
                            "title": key,
                            "description": text,
                            "company": channel,
                            "email": next(iter(re.findall(email_regex, text)), ""),
                            "phone": next(iter(re.findall(phone_regex, text)), ""),
                            "link": next(iter(re.findall(link_regex, text)), ""),
                            "date": msg.date.astimezone(timezone.utc).strftime("%Y-%m-%d") if msg.date else "",
                            "time": msg.date.astimezone(timezone.utc).strftime("%H:%M") if msg.date else ""
                        }
                        jobs.append(job)
                        print(f"✅ وظيفة جديدة: {key} من {channel}")
                        break

        except Exception as e:
            print(f"❌ خطأ في {channel}: {e}")

    save_jobs(jobs)

# ====== التشغيل ======
async def main():
    await client.connect()

    if not await client.is_user_authorized():
        raise RuntimeError("❌ Session غير صالحة أو لم يتم تسجيل الدخول بها مسبقًا")

    await fetch_jobs()
    await client.disconnect()

asyncio.run(main())
