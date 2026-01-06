from telethon import TelegramClient, events
import json
import asyncio
import re

# --- ضع بياناتك الصحيحة هنا ---
import os

# --- قراءة api_id و api_hash من المتغيرات البيئية ---
api_id = int(os.environ.get("API_ID", "0"))
api_hash = os.environ.get("API_HASH", "")


# --- القنوات اللي تريد البحث فيها ---
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

# --- الكلمات المفتاحية الموسعة للبحث ---
keywords = [
    "مهندس", "engineer", "ميكانيكي", "ميكانيكا", "وظيفة",
    "مهندس ميكانيكي", "Mechanical Engineer", "mechanical engineer",
    "ميكانيكية", "ميكانيك", "مهندسة ميكانيكية",
    "تصميم ميكانيكي", "Mechanical Design", "Maintenance Engineer", "مهندس صيانة",
    "مهندس انتاج", "Production Engineer", "مهندس تصنيع", "مهندس مشاريع"
]

# --- Regex لاستخراج البريد، الجوال، الروابط ---
email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
phone_regex = r"(?:\+966|0)?5\d{8}"
link_regex = r"(https?://[^\s]+)"

# --- تهيئة العميل ---
client = TelegramClient("session", api_id, api_hash)

# --- دالة لحفظ البيانات في jobs.json ---
def save_job(job):
    try:
        with open("jobs.json", "r", encoding="utf-8") as f:
            jobs = json.load(f)
    except FileNotFoundError:
        jobs = []

    jobs.append(job)
    with open("jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

# --- التعامل مع كل رسالة جديدة في القنوات ---
@client.on(events.NewMessage(chats=channels))
async def new_job(event):
    text = getattr(event.message, "message", "")
    if text:
        for key in keywords:
            if key.lower() in text.lower():
                job = {
                    "title": key,
                    "description": text,
                    "company": getattr(event.chat, "username", "") or getattr(event.chat, "title", ""),
                    "email": next(iter(re.findall(email_regex, text)), ""),
                    "phone": next(iter(re.findall(phone_regex, text)), ""),
                    "link": next(iter(re.findall(link_regex, text)), ""),
                    "date": str(event.message.date.date()) if event.message.date else "",
                    "time": str(event.message.date.time()) if event.message.date else ""
                }
                save_job(job)
                print(f"تم إضافة وظيفة جديدة: {key} من {job['company']}")
                break

# --- جلب آخر 50 رسالة عند بداية التشغيل ---
async def fetch_last_messages():
    for channel in channels:
        try:
            entity = await client.get_input_entity(channel)
            messages = await client.get_messages(entity, limit=50)
            for message in messages:
                text = getattr(message, "message", "")
                if text:
                    for key in keywords:
                        if key.lower() in text.lower():
                            job = {
                                "title": key,
                                "description": text,
                                "company": channel,
                                "email": next(iter(re.findall(email_regex, text)), ""),
                                "phone": next(iter(re.findall(phone_regex, text)), ""),
                                "link": next(iter(re.findall(link_regex, text)), ""),
                                "date": str(message.date.date()) if message.date else "",
                                "time": str(message.date.time()) if message.date else ""
                            }
                            save_job(job)
                            print(f"تم استرجاع وظيفة قديمة: {key} من {channel}")
                            break
        except Exception as e:
            print(f"فشل الوصول للقناة {channel}: {e}")

# --- تشغيل السكربت ---
async def main():
    async with client:
        print("تم تشغيل السكربت، يجلب آخر الرسائل ثم ينتظر الجديد...")
        await fetch_last_messages()
        await client.run_until_disconnected()

asyncio.run(main())
