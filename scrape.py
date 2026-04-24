from telethon.sync import TelegramClient
import requests

api_id = 33370509
api_hash = "669af6caebf2aca264b16cf8b40d37b2"
session = "session0"

client = TelegramClient(session, api_id, api_hash)

def scrape_group(chat_id):
    users = []

    client.start()

    print("[SCRAPE] mulai...")

    for u in client.iter_participants(chat_id):
        if not u.bot:
            users.append({
                "id": u.id,
                "name": u.first_name or "User"
            })

    print(f"[SCRAPE] total: {len(users)}")

    requests.post("http://127.0.0.1:5000/save", json={
        "chat_id": str(chat_id),
        "users": users
    })

    print("[SCRAPE] selesai")

if __name__ == "__main__":
    chat_id = -1002430300514  # ganti group ID
    scrape_group(chat_id)
