from telethon import TelegramClient
import json
import asyncio
import re
import os
from datetime import timezone

# ====== بيانات سرية من GitHub Secrets ======
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

client = TelegramClient("session", api_id, api_hash)

# ====== تحميل الوظائف الحالية ======
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

# ====== جلب الرسائل ======
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
                            "date": msg.date.astimezone(timezone.utc).strftime("%Y-%m-%d"),
                            "time": msg.date.astimezone(timezone.utc).strftime("%H:%M")
                        }
                        jobs.append(job)
                        print(f"✅ وظيفة جديدة: {key} من {channel}")
                        break

        except Exception as e:
            print(f"❌ خطأ في {channel}: {e}")

    save_jobs(jobs)

# ====== التشغيل ======
async def main():
    async with client:
        await fetch_jobs()

asyncio.run(main())
