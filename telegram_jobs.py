from telethon import TelegramClient, events
import json
import asyncio

# --- ضع بياناتك الصحيحة هنا ---
api_id = 36317877  # ضع API ID الخاص بك
api_hash = "c9a072cf37b7fdf312c79f4ab7d528d4"  # ضع API HASH الخاص بك

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
            if key.lower() in text.lower():  # للتأكد من البحث بدون حساسية للحروف
                job = {
                    "title": key,
                    "description": text,
                    "source": event.chat.username
                }
                save_job(job)
                print(f"تم إضافة وظيفة جديدة: {key} من {event.chat.username}")
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
                                "source": channel
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
