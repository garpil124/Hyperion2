import pytz
import os
import requests
import time
import threading
import asyncio
import json
import re
import random   # 🔥 WAJIB
import html     # 🔥 biar ga error escape
import subprocess
import zipfile
from queue import Queue
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CommandHandler, CallbackQueryHandler
from telethon import TelegramClient
import database0
from user import register_menu
from emoji import build_emoji
from fitur import register_fitur
from rekab import register_rekab
from absen import register_absen
import pesan

PAGE_SIZE = 10

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

TOKEN = "8307438695:AAGXU7CXaf4MjWo_8-_kwefs_SS03MDYJqU"
API_URL = "http://127.0.0.1:5000/get"
TARGET_CHATS = [-1002430300514]
FORCE_GROUP = -1002430300514   # 🔥 WAJIB (buat cek join)
FORCE_LINK = "https://t.me/officialhyperion"
OWNER_IDS = [8209644174, 5744453710, 8730304700]
PARTNER_FILE = "partner.json0"
SETTING_FILE = "setting.json0"
SETTING_FILE = "setting.json0"
QUEUE_FILE = "queue.json0"
AUTO_TAG_FILE = "autotag.json0"
BUTTON_FILE = "buttons.json0"
BACKUP_DIR = "backups0"
SERVICE_NAME = "Hyperionn-"
api_id = 35873646
api_hash = "3eaf9faf00e794125b7330d4978ffdce"
client = TelegramClient("session0", api_id, api_hash)
client.start()
task_queue = Queue()
running_task = False  # 🔥 ANTI DOUBLE TASK

# ================= SETTING =================
def load_setting():
    try:
        with open(SETTING_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_setting(data):
    with open(SETTING_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ================= FILE (JANGAN DIUBAH) =================
def load_partner():
    if not os.path.exists(PARTNER_FILE):
        return []

    try:
        with open(PARTNER_FILE, "r") as f:
            data = json.load(f)

        # 🔥 pastikan list
        if not isinstance(data, list):
            return []

        # 🔥 filter hanya data valid (dict)
        clean_data = []
        for p in data:
            if isinstance(p, dict):
                clean_data.append(p)

        return clean_data

    except Exception as e:
        print("❌ load error:", e)
        return []


def save_partner(data):
    try:
        # 🔥 hanya simpan yang valid
        clean_data = [p for p in data if isinstance(p, dict)]

        with open(PARTNER_FILE, "w") as f:
            json.dump(clean_data, f, indent=2)

        print("✅ KE SAVE:", clean_data)

    except Exception as e:
        print("❌ save error:", e)

# ================= BUTTON FILE (BARU) =================
def load_buttons():
    if not os.path.exists(BUTTON_FILE):
        return {}
    try:
        with open(BUTTON_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print("❌ load button error:", e)
        return {}

def save_buttons(data):
    try:
        with open(BUTTON_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print("✅ BUTTON KE SAVE:", data)
    except Exception as e:
        print("❌ save button error:", e)

def load_autotag():
    global auto_data
    if not os.path.exists(AUTO_TAG_FILE):
        auto_data = {}
        return
    try:
        with open(AUTO_TAG_FILE, "r") as f:
            auto_data = json.load(f)
    except:
        auto_data = {}

def save_autotag():
    with open(AUTO_TAG_FILE, "w") as f:
        json.dump(auto_data, f, indent=2)

def save_last_group(update, context):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id

    if chat_id < 0:
        if user_id not in auto_data:
            auto_data[user_id] = {}

        auto_data[user_id]["chat_id"] = chat_id
        save_autotag()

# ================= PERSISTENT QUEUE =================
def save_queue():
    try:
        data = []
        while not task_queue.empty():
            data.append(task_queue.get())
        with open(QUEUE_FILE, "w") as f:
            json.dump(data, f)
        for item in data:
            task_queue.put(item)
    except:
        pass

def load_queue():
    try:
        with open(QUEUE_FILE, "r") as f:
            data = json.load(f)
            for item in data:
                task_queue.put(tuple(item))
    except:
        pass

# ================= GLOBAL =================
manual_setup = {}
stop_flag = {}
manual_messages = {}
auto_data = {}
custom_buttons = load_buttons()  # 🔥 PENTING (BUKAN load_partner)

# 🔥 TAMBAHAN WAJIB
recent_messages = set()
rate_limit = {}
last_activity = {}

# ================= UTIL =================

def normalize_link(link):
    link = link.strip()
    link = link.replace("https://", "").replace("http://", "")
    link = link.replace("t.me/", "")
    return link.lower()


def get_group_name(link):
    username = normalize_link(link)

    # 1. TELETHON (kalau ada cache)
    try:
        entity = loop.run_until_complete(client.get_entity(username))
        if entity.title:
            return entity.title
    except Exception as e:
        print("❌ telethon fail:", e)

    # 2. SCRAPE PREVIEW (kayak Telegram preview)
    try:
        url = f"https://t.me/{username}"
        res = requests.get(url, timeout=5)

        match = re.search(r'<meta property="og:title" content="([^"]+)"', res.text)
        if match:
            return match.group(1)

    except Exception as e:
        print("❌ scrape fail:", e)

    return "Unknown Group"

def add_livechat(update, context):
    if update.effective_user.id not in OWNER_IDS:
        return

    if not context.args:
        return update.message.reply_text(
            "❌ kirim link\nContoh: /addlivechat https://t.me/xxxx"
        )

    link = context.args[0]

    if not link.startswith("https://t.me/"):
        return update.message.reply_text("❌ link harus https://t.me/")

    data = load_setting()
    data["livechat"] = link
    save_setting(data)

    update.message.reply_text("✅ Live chat disimpan")

def del_livechat(update, context):
    if update.effective_user.id not in OWNER_IDS:
        return

    data = load_setting()
    data.pop("livechat", None)
    save_setting(data)

    update.message.reply_text("✅ Live chat dihapus")

# ================= MANUAL BACKUP =================
def backup_cmd(update, context):
    global LAST_BACKUP

    user_id = update.effective_user.id

    if user_id not in OWNER_IDS:
        update.message.reply_text("❌ bukan owner")
        return

    try:
        update.message.reply_text("📦 membuat backup...")

        name = f"manual_backup_{int(time.time())}.zip"

        with zipfile.ZipFile(name, 'w', zipfile.ZIP_DEFLATED) as z:

            for f in CORE_FILES:
                if os.path.exists(f):
                    z.write(f)

            if os.path.exists("database0"):
                for root, _, files2 in os.walk("database0"):
                    for f in files2:
                        z.write(os.path.join(root, f))

        LAST_BACKUP = name  # 🔥 penting biar rollback bisa pakai ini

        with open(name, "rb") as f:
            context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=name
            )

        update.message.reply_text("✅ backup manual selesai")

    except Exception as e:
        update.message.reply_text(f"❌ backup gagal: {e}")

# ================= COMMAND =================
def add_partner(update, context):
    if update.effective_user.id not in OWNER_IDS:
        return

    # ================= VALIDASI INPUT =================
    if not update.message or not update.message.text:
        update.message.reply_text("❌ format: /addpartner nama link")
        return

    # ================= AMBIL FULL TEXT =================
    text = update.message.text

    # hapus command
    if text.startswith("/addpartner"):
        text = text.replace("/addpartner", "", 1).strip()

    if not text:
        update.message.reply_text("❌ format:\n/addpartner nama link\natau /addpartner link")
        return

    data = load_partner()

    # ================= PARSING BENAR (AMBIL LINK DARI BELAKANG) =================
    parts = text.rsplit(" ", 1)

    if len(parts) == 2:
        name_input, link = parts
    else:
        link = parts[0]
        name_input = None

    # ================= VALIDASI LINK =================
    if not link.startswith("http"):
        update.message.reply_text("❌ link tidak valid")
        return

    # ================= CEK DUPLIKAT =================
    for p in data:
        if link in p.get("link", ""):
            update.message.reply_text("⚠️ sudah ada")
            return

    # ================= PRIVATE LINK =================
    if "t.me/+" in link or "joinchat" in link:
        try:
            name = name_input if name_input else get_group_name(link)

            data.append({
                "link": link,
                "username": "private",
                "name": name
            })

            save_partner(data)
            update.message.reply_text(f"✅ Partner private ditambah:\n{name}")

        except Exception as e:
            update.message.reply_text(f"❌ Gagal add private\n{e}")

        return

    # ================= PUBLIC LINK =================
    username = normalize_link(link)

    name = name_input if name_input else get_group_name(link)

    data.append({
        "link": f"https://t.me/{username}",
        "username": username,
        "name": name
    })

    save_partner(data)

    update.message.reply_text(f"✅ Partner ditambah:\n{name}")


def del_partner(update, context):
    if update.effective_user.id not in OWNER_IDS:
        return

    if not context.args:
        update.message.reply_text("❌ format: /delpartner link")
        return

    link = context.args[0]
    data = load_partner()

    new_data = []

    for p in data:
        if link in p.get("link", ""):
            continue
        new_data.append(p)

    save_partner(new_data)
    update.message.reply_text("✅ Partner dihapus")


def tagall_cmd(update, context):
    chat = update.effective_chat
    user = update.effective_user

    # ❌ Jangan di private
    if chat.type == "private":
        return

    # 🔥 CEK ADMIN
    try:
        member = context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ["administrator", "creator"]:
            update.message.reply_text("❌ Khusus admin")
            return
    except:
        return

    # 🔥 TAMBAHAN INI (WAJIB)
    user_id = str(update.effective_user.id)

    if user_id not in auto_data:
        auto_data[user_id] = {}

    auto_data[user_id]["chat_id"] = chat.id
    save_autotag()

    # ================= LANJUT KODE LU =================
    text = " ".join(context.args)

    if text:
        manual_setup[chat.id] = {"msg": text, "mode": "text"}
    elif update.message.reply_to_message:
        manual_setup[chat.id] = {
            "msg": update.message.reply_to_message,
            "mode": "reply"
        }
    else:
        update.message.reply_text("❌ Isi teks atau reply pesan")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("2 menit", callback_data="dur_2"),
         InlineKeyboardButton("5 menit", callback_data="dur_5")],
        [InlineKeyboardButton("10 menit", callback_data="dur_10"),
         InlineKeyboardButton("30 menit", callback_data="dur_30")],
        [InlineKeyboardButton("60 menit", callback_data="dur_60"),
         InlineKeyboardButton("Unlimited", callback_data="dur_unli")]
    ])

    update.message.reply_text(
        "⏱ Pilih durasi:",
        reply_markup=keyboard
    )

def cancel_cmd(update, context):
    global stop_flag

    chat = update.effective_chat
    user = update.effective_user

    # ❌ Jangan boleh di private
    if chat.type == "private":
        return

    # 🔥 CEK ADMIN
    try:
        member = context.bot.get_chat_member(chat.id, user.id)
        if member.status not in ["administrator", "creator"]:
            update.message.reply_text("❌ Khusus admin")
            return
    except:
        return

    # 🔥 STOP
    stop_flag[chat.id] = True

    try:
        context.bot.send_message(chat.id, "⛔ Tagall dihentikan")
    except:
        pass
        

# ================= LIST COMMAND =================
def list_partner(update, context):
    print("🔥 list_partner kepanggil")

    if update.effective_user.id not in OWNER_IDS:
        return

    send_partner_page_message(update, context, 0)


# ================= SEND (FROM COMMAND) =================
def send_partner_page_message(update, context, page):
    data = load_partner()

    if not data:
        update.message.reply_text("❌ kosong")
        return

    total = len(data)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    text = f"📋 LIST PARTNER\nHalaman {page+1}\n\n"

    buttons_list = []

    # ================= LIST DATA =================
    for i, p in enumerate(data[start:end], start + 1):
        idx = start + (i - start - 1)

        text += f"{i}. {p.get('name','-')}\n{p.get('link','-')}\n\n"

        # tombol edit per item
        buttons_list.append([
            InlineKeyboardButton("✏️ Edit", callback_data=f"edit_menu_{idx}")
        ])

    # ================= PAGINATION =================
    nav_buttons = build_buttons(page, total)

    # gabung tombol edit + pagination
    keyboard = buttons_list + nav_buttons.inline_keyboard

    update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= SEND (FROM CALLBACK MENU) =================
def send_partner_page_callback(query, context, page):
    data = load_partner()

    if not data:
        query.message.reply_text("❌ kosong")
        return

    total = len(data)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    text = f"📋 LIST PARTNER\nHalaman {page+1}\n\n"

    for i, p in enumerate(data[start:end], start + 1):
        text += f"{i}. {p.get('name','-')}\n{p.get('link','-')}\n\n"

    buttons = build_buttons(page, total)

    query.message.reply_text(text, reply_markup=buttons)


def build_buttons(page, total):
    buttons = []

    data = load_partner()

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    # ================= EDIT BUTTON PER ITEM =================
    for i in range(start, min(end, total)):
        buttons.append([
            InlineKeyboardButton(
                f"✏️ Edit {i+1}",
                callback_data=f"edit_menu_{i}"
            )
        ])

    # ================= NAVIGATION =================
    nav = []

    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"partner_{page-1}"))

    if end < total:
        nav.append(InlineKeyboardButton("➡️ Next", callback_data=f"partner_{page+1}"))

    if nav:
        buttons.append(nav)

    # ================= CLOSE =================
    buttons.append([
        InlineKeyboardButton("❌ Close", callback_data="partner_close")
    ])

    return InlineKeyboardMarkup(buttons)


# ================= CALLBACK PARTNER =================
def partner_callback(update, context):
    print("🔥 CALLBACK PARTNER")

    query = update.callback_query
    query.answer()

    data = query.data
    print("DATA:", data)

    data_list = load_partner()

    # ================= CLOSE =================
    if data == "partner_close":
        query.message.delete()
        return

    # ================= OPEN EDIT MENU =================
    if data.startswith("edit_menu_"):
        idx = int(data.split("_")[2])

        context.user_data["edit"] = {
            "idx": idx,
            "field": "name"
        }

        query.message.reply_text("✏️ kirim format: NAMA LINK")
        return

    # ================= PAGINATION =================
    try:
        page = int(data.split("_")[1])
    except:
        return

    total = len(data_list)
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    text = f"📋 LIST PARTNER\nHalaman {page+1}\n\n"

    for i, p in enumerate(data_list[start:end], start + 1):
        text += f"{i}. {p.get('name','-')}\n{p.get('link','-')}\n\n"

    buttons = build_buttons(page, total)

    query.edit_message_text(text, reply_markup=buttons)

def handle_edit(update, context):
    if "edit" not in context.user_data:
        return

    idx = context.user_data["edit"]["idx"]
    data = load_partner()

    try:
        name, link = update.message.text.split(" ", 1)

        data[idx] = {
            "name": name,
            "link": link,
            "username": normalize_link(link)
        }

        save_partner(data)

        update.message.reply_text("✅ updated")

        del context.user_data["edit"]

    except:
        update.message.reply_text("❌ format salah")

def addbuttontag_cmd(update, context):
    print("🔥 addbuttontag kepanggil")

    chat = update.effective_chat
    user = update.effective_user

    # 🔥 HARUS PRIVATE
    if chat.type != "private":
        update.message.reply_text("❌ Gunakan di private bot")
        return

    # 🔥 OWNER ONLY
    if user.id not in OWNER_IDS:
        update.message.reply_text("❌ Khusus owner")
        return

    # 🔥 FORMAT
    if not context.args:
        update.message.reply_text("Format:\n/addbuttontag NAMA - LINK")
        return

    text = " ".join(context.args)

    if "-" not in text:
        update.message.reply_text("Format:\n/addbuttontag NAMA - LINK")
        return

    name, link = text.split("-", 1)
    name = name.strip()
    link = link.strip()

    # 🔥 LOOP SEMUA TARGET CHAT
    for gc_id in TARGET_CHATS:
        custom_buttons[str(gc_id)] = {
            "name": name,
            "link": link
        }

    save_partner(custom_buttons)

    update.message.reply_text(
        f"✅ Button diset ke {len(TARGET_CHATS)} grup\n{name} -> {link}"
    )


def fancy_name(text):
    fonts = [
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
         "𝑨𝑩𝑪𝑫𝑬𝑭𝑮𝑯𝑰𝑱𝑲𝑳𝑴𝑵𝑶𝑷𝑸𝑹𝑺𝑻𝑼𝑽𝑾𝑿𝒀𝒁abcdefghijklmnopqrstuvwxyz"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
         "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩abcdefghijklmnopqrstuvwxyz"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
         "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉abcdefghijklmnopqrstuvwxyz"),
    ]

    normal, fancy = random.choice(fonts)
    return text.translate(str.maketrans(normal, fancy))

def autotag_menu(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    if update.effective_user.id not in OWNER_IDS:
        return

    if update.effective_chat.type != "private":
        update.message.reply_text("❌ Gunakan di private")
        return

    if not context.args:
        update.message.reply_text("❌ Contoh:\n/autotag pesan")
        return

    msg = " ".join(context.args)

    if user_id not in auto_data:
        auto_data[user_id] = {}

    auto_data[user_id].update({
        "text": msg,
        "hour": None,
        "minute": 0,
        "duration": 60,
        "active": False,
        "last_run": None,
        "chat_id": update.effective_chat.id
    })

    save_autotag()

    buttons, row = [], []
    for i in range(24):
        row.append(InlineKeyboardButton(f"{i:02d}:00", callback_data=f"setjam_{i}"))
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    update.message.reply_text(
        "🕒 PILIH JAM AUTO TAGALL",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

def pilih_jam(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.from_user.id not in OWNER_IDS:
        return

    user_id = str(query.from_user.id)

    if user_id not in auto_data:
        query.edit_message_text("❌ Session hilang")
        return

    jam = int(query.data.split("_")[1])

    auto_data[user_id]["hour"] = jam
    save_autotag()

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱ 10 MENIT", callback_data="autodur_10"),
            InlineKeyboardButton("⏱ 15 MENIT", callback_data="autodur_15")
        ],
        [
            InlineKeyboardButton("⏱ 30 MENIT", callback_data="autodur_30"),
            InlineKeyboardButton("⏱ 60 MENIT", callback_data="autodur_60")
        ],
        [
            InlineKeyboardButton("⏱ 120 MENIT", callback_data="autodur_120")
        ]
    ])

    query.edit_message_text(
        f"✅ JAM: {jam:02d}:00\n\nPilih durasi:",
        reply_markup=keyboard
    )

def pilih_durasi(update: Update, context: CallbackContext):
    query = update.callback_query

    try:
        query.answer()
    except:
        pass

    if query.from_user.id not in OWNER_IDS:
        return

    user_id = str(query.from_user.id)

    if user_id not in auto_data:
        query.edit_message_text("❌ Session hilang")
        return

    dur = int(query.data.split("_")[1])

    auto_data[user_id]["duration"] = dur
    auto_data[user_id]["active"] = True

    save_autotag()

    query.edit_message_text(
        f"🚀 AUTO TAG AKTIF\n\n"
        f"🕒 Jam: {auto_data[user_id]['hour']:02d}:00\n"
        f"⏱ Durasi: {dur} menit\n\n"
        f"Bot jalan tiap hari otomatis."
    )

def onauto(update, context):
    user_id = str(update.effective_user.id)

    if user_id not in auto_data:
        update.message.reply_text("❌ Belum ada setting auto tag")
        return

    auto_data[user_id]["active"] = True
    save_autotag()
    update.message.reply_text("🟢 AUTO TAG AKTIF")


def offauto(update, context):
    user_id = str(update.effective_user.id)

    if user_id not in auto_data:
        update.message.reply_text("❌ Belum ada setting auto tag")
        return

    auto_data[user_id]["active"] = False
    save_autotag()
    update.message.reply_text("🔴 AUTO TAG DIMATIKAN")


def clearauto(update, context):
    user_id = str(update.effective_user.id)

    if user_id in auto_data:
        auto_data.pop(user_id)
        save_autotag()
        update.message.reply_text("🧹 DATA AUTO DIHAPUS")
    else:
        update.message.reply_text("❌ Tidak ada data auto")


def auto_tag_worker(context):
    while True:
        try:
            now = time.localtime()
            tanggal = time.strftime("%d-%m-%Y")

            for user_id, data in list(auto_data.items()):

                try:
                    if not data.get("active"):
                        continue

                    if data.get("hour") is None:
                        continue

                    if now.tm_hour != data["hour"] or now.tm_min != data["minute"]:
                        continue

                    target_chat = int(data.get("chat_id", user_id))
                    text = data.get("text", "AUTO TAGALL")

                    # 🔥 ANTI DUPLICATE
                    msg_key = f"{target_chat}_{text}_{tanggal}"
                    if msg_key in recent_messages:
                        continue
                    recent_messages.add(msg_key)

                    # 🔥 RATE LIMIT PER CHAT
                    if rate_limit.get(target_chat, 0) > 5:
                        continue

                    # 🔥 LOG (SAFE)
                    try:
                        context.bot.send_message(
                            LOG_CHAT_ID,
                            f"🚀 AUTO TAG JALAN\n\n"
                            f"📅 {tanggal}\n"
                            f"👤 {user_id}\n"
                            f"🎯 {target_chat}\n"
                            f"🕒 {data['hour']:02d}:{data['minute']:02d}"
                        )
                    except Exception as e:
                        print("LOG ERROR:", e)

                    # 🔥 SMART RETRY
                    for attempt in range(5):
                        try:
                            delay = random.uniform(2, 5) + (attempt * random.uniform(1, 3))
                            time.sleep(delay)

                            duration = data.get("duration", 60) * 60

                            run_tagall_manual(
                                context,
                                target_chat,
                                text,
                                "normal",
                                duration
                            )

                            # turunin limit kalau sukses
                            rate_limit[target_chat] = max(0, rate_limit.get(target_chat, 0) - 1)

                            break

                        except Exception as e:
                            print(f"[RETRY {attempt+1}] ERROR:", e)

                            # 🔥 DETECT FLOOD
                            if "Too Many Requests" in str(e):
                                rate_limit[target_chat] = rate_limit.get(target_chat, 0) + 1
                                time.sleep(random.uniform(5, 10))

                            # ❌ FAIL TOTAL
                            if attempt == 4:
                                print("❌ GAGAL TOTAL:", target_chat)

                    # 🔥 MARK SUDAH JALAN
                    auto_data[user_id]["last_run"] = tanggal

                    try:
                        save_autotag()
                    except Exception as e:
                        print("SAVE ERROR:", e)

                except Exception as e:
                    print("USER LOOP ERROR:", e)

            # 🔥 AUTO CLEAR
            if len(recent_messages) > 500:
                recent_messages.clear()

            # 🔥 CLEAN RATE LIMIT
            for chat in list(rate_limit.keys()):
                if time.time() - last_activity.get(chat, 0) > 60:
                    rate_limit[chat] = 0

        except Exception as e:
            print("WORKER FATAL ERROR:", e)

        # 🔥 FIXED SLEEP (ANTI CPU SPAM)
        time.sleep(5)

# ================= HANDLE DURASI =================
def handle_durasi(update, context):
    query = update.callback_query
    chat_id = query.message.chat.id

    # 🔥 ANTI ERROR CALLBACK EXPIRED
    try:
        query.answer()
    except:
        pass

    if chat_id not in manual_setup:
        query.edit_message_text("❌ Session hilang")
        return

    data = query.data.split("_")[1]

    durasi_map = {
        "2": 120,
        "5": 300,
        "10": 600,
        "30": 1800,
        "60": 3600,
        "unli": None
    }

    duration = durasi_map.get(data)

    setup = manual_setup[chat_id]
    msg = setup["msg"]
    mode = setup["mode"]

    query.edit_message_text("🚀 Tagall manual dimulai...")

    import threading
    t = threading.Thread(
        target=run_tagall_manual,
        args=(context, chat_id, msg, mode, duration),
        daemon=True
    )
    t.start()

# ================= RUN MANUAL TAGALL =================
def run_tagall_manual(context, chat_id, msg, mode, duration):
    global stop_flag, manual_messages, last_activity

    import random
    import time
    import html
    import re
    from collections import deque

    from emoji import build_emoji  

    stop_flag[chat_id] = False  
    manual_messages[chat_id] = []  

    # ================= GET MEMBERS =================
    try:
        members = get_members(chat_id)
    except Exception as e:
        print("GET MEMBERS ERROR:", e)
        return

    if not members:  
        print("❌ MEMBERS KOSONG")
        return  

    # ================= QUEUE SYSTEM =================
    user_ids = list(members.keys())
    random.shuffle(user_ids)
    queue = deque(user_ids)

    BATCH_SIZE = 3
    base_delay = 2.5
    current_delay = base_delay

    start_time = time.time()  
    sent = 0  
    stopped = False  

    btn = custom_buttons.get(str(chat_id))  

    # ================= LOOP =================  
    while queue:  

        if stop_flag.get(chat_id):  
            stopped = True  
            break  

        if duration and time.time() - start_time > duration:  
            break  

        batch = []

        # 🔥 ambil batch dari queue
        for _ in range(BATCH_SIZE):
            if queue:
                batch.append(queue.popleft())

        if not batch:
            break  

        # 🔥 EMOJI
        try:
            emoji_text = build_emoji()
        except:
            emoji_text = ""

        # 🔥 MENTION
        mention_list = []  
        for uid in batch:  
            name = html.escape(members.get(uid, "user"))  
            fancy = fancy_name(name)  
            mention_list.append(f'<a href="tg://user?id={uid}">{fancy}</a>')  

        mention_text = " ".join(mention_list)  

        final_text = f"✦ {msg.upper()} ✦\n\n{emoji_text}\n\n{mention_text}\n\n✦🌑✦"  

        if btn:  
            keyboard = InlineKeyboardMarkup([  
                [InlineKeyboardButton(btn["name"], url=btn["link"])]  
            ])  
        else:  
            keyboard = None  

        try:  
            sent_msg = context.bot.send_message(  
                chat_id,  
                final_text,  
                parse_mode="HTML",  
                reply_markup=keyboard  
            )  

            manual_messages[chat_id].append(sent_msg.message_id)  
            sent += len(batch)  

            last_activity[chat_id] = time.time()  

            # 🔥 sukses → delay normal + random
            time.sleep(current_delay + random.uniform(0.5, 1.5))  

        except Exception as e:  
            err = str(e)

            # ================= FLOOD HANDLER =================
            if "Retry in" in err:
                try:
                    wait = int(re.search(r"Retry in (\d+)", err).group(1))
                    print(f"⚠️ FLOOD → WAIT {wait}s")

                    # 🔥 pause panjang (anti spam lanjut)
                    time.sleep(wait + random.uniform(1, 3))

                    # 🔥 masukkan lagi batch ke depan queue (auto retry)
                    for uid in batch:
                        queue.appendleft(uid)

                    # 🔥 slowdown agresif
                    current_delay += 2  

                except:
                    time.sleep(5)

            else:
                print("SEND ERROR:", e)
                time.sleep(2)

        # ================= ADAPTIVE CONTROL =================

        if sent > 50:
            current_delay = 3.5

        if sent > 200:
            current_delay = 5

        if sent > 500:
            current_delay = 6

        # 🔥 safety tambahan biar gak brutal
        time.sleep(random.uniform(0.5, 1.5))

    # ================= DONE =================  

    text_done = "⛔ Tagall dihentikan" if stopped else f"✅ Tagall selesai\n👥 Total tag: {sent}"  

    if btn:  
        keyboard_clear = InlineKeyboardMarkup([  
            [InlineKeyboardButton(btn["name"], url=btn["link"])],  
            [InlineKeyboardButton("🧹 CLEAR CHAT", callback_data="manual_clear")]  
        ])  
    else:  
        keyboard_clear = InlineKeyboardMarkup([  
            [InlineKeyboardButton("🧹 CLEAR CHAT", callback_data="manual_clear")]  
        ])  

    context.bot.send_message(  
        chat_id,  
        text_done,  
        reply_markup=keyboard_clear  
    )  

    print(f"🔥 TAGALL HARDCORE DONE | Chat: {chat_id} | Sent: {sent}")
              
   # ================= AUTO CLEAR =================  
    def auto_clear():  
        time.sleep(120)  

        msgs = manual_messages.get(chat_id, []).copy()  

        for msg_id in msgs:
            try:
                context.bot.delete_message(chat_id, msg_id)
            except:
                pass

        try:
            context.bot.delete_message(chat_id, done_msg.message_id)
        except:
            pass

        manual_messages[chat_id] = []

    threading.Thread(target=auto_clear, daemon=True).start()
            
            

def button_handler(update, context):
    query = update.callback_query

    try:
        query.answer()
    except:
        pass

    chat_id = query.message.chat_id

    if query.data == "manual_clear":
        msgs = manual_messages.get(chat_id, [])

        for msg_id in msgs:
            try:
                context.bot.delete_message(chat_id, msg_id)
            except:
                pass

        try:
            context.bot.delete_message(chat_id, query.message.message_id)
        except:
            pass

        manual_messages[chat_id] = []
                  
# ================= OWNER SET =================

def bot_on(update, context):
    global WORKER_ACTIVE
    if update.effective_user.id not in OWNER_IDS or update.effective_chat.type != "private":
        return

    WORKER_ACTIVE = True
    update.message.reply_text("✅ Tagall dibuka (ON)")


def bot_off(update, context):
    global WORKER_ACTIVE
    if update.effective_user.id not in OWNER_IDS or update.effective_chat.type != "private":
        return

    WORKER_ACTIVE = False
    update.message.reply_text("❌ Tagall dimatikan (OFF)")


def help_owner(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if user_id not in OWNER_IDS:
        return

    text = (
        "👑 𝗢𝗪𝗡𝗘𝗥 𝗣𝗔𝗡𝗘𝗟\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "🖼️ 𝗠𝗘𝗗𝗜𝗔\n"
        "➜ /addpict  (pasang foto)\n"
        "➜ /delpict  (hapus foto)\n\n"

        "👤 𝗣𝗘𝗡𝗚𝗔𝗧𝗨𝗥𝗔𝗡\n"
        "➜ /addpj    (tambah PJ)\n"
        "➜ /delpj    (hapus PJ)\n\n"

        "📋 𝗣𝗔𝗥𝗧𝗡𝗘𝗥\n"
        "➜ /listpartner\n\n"

        "📢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧\n"
        "➜ /bc pesan\n\n"
    
        "💌 𝗟𝗜𝗩𝗘 𝗖𝗛𝗔𝗧\n"
        "➜ /live chat\n"
        "➜ /addlivechat\n"
        "➜ /dellivecaht\n\n"

        "🏷️ 𝗧𝗔𝗚𝗔𝗟𝗟\n"
        "➜ /tagall pesan\n"
        "➜ /addbuttontag nama|link\n\n"

        "🤖 𝗔𝗨𝗧𝗢 𝗧𝗔𝗚\n"
        "➜ /autotag pesan\n"
        "➜ /onauto\n"
        "➜ /offauto\n"
        "➜ /clearauto\n\n"

        "⚙️ 𝗦𝗜𝗦𝗧𝗘𝗠\n"
        "➜ /on   (aktifkan)\n"
        "➜ /off  (matikan)\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ Klik tombol / pakai command manual"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼️ Add", callback_data="cmd_addpict"),
            InlineKeyboardButton("🗑️ Del", callback_data="cmd_delpict")
        ],
        [
            InlineKeyboardButton("👤 Add PJ", callback_data="cmd_addpj"),
            InlineKeyboardButton("❌ Del PJ", callback_data="cmd_delpj")
        ],
        [
            InlineKeyboardButton("📋 Partner", callback_data="cmd_listpartner")
        ],
        [
            InlineKeyboardButton("📢 Broadcast", callback_data="cmd_bc")
        ],
        [
            InlineKeyboardButton("🏷️ Tagall", callback_data="cmd_tagall")
        ],
        [
            InlineKeyboardButton("💬 Add LiveChat", callback_data="cmd_addlivechat"),
            InlineKeyboardButton("🗑️ Del LiveChat", callback_data="cmd_dellivechat")
        ],
        [
            InlineKeyboardButton("🤖 AutoTag", callback_data="cmd_autotag")
        ],
        [
            InlineKeyboardButton("🟢 ON", callback_data="cmd_on"),
            InlineKeyboardButton("🔴 OFF", callback_data="cmd_off")
        ],
        [
            InlineKeyboardButton("👑 Creator", url="https://t.me/Brsik23")
        ]
    ])

    update.message.reply_text(text, reply_markup=keyboard)
    

def add_pict(update, context):
    if update.effective_user.id not in OWNER_IDS or update.effective_chat.type != "private":
        return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        update.message.reply_text("❌  reply foto dengan /addpict")
        return
    file_id = update.message.reply_to_message.photo[-1].file_id
    data = load_setting()
    data["start_pict"] = file_id
    save_setting(data)
    update.message.reply_text("✅  foto disimpan")


def del_pict(update, context):
    if update.effective_user.id not in OWNER_IDS or update.effective_chat.type != "private":
        return
    data = load_setting()
    data.pop("start_pict", None)
    save_setting(data)
    update.message.reply_text("✅  foto dihapus")


def add_pj(update, context):
    if update.effective_user.id not in OWNER_IDS or update.effective_chat.type != "private":
        return
    username = context.args[0].replace("@", "")
    data = load_setting()
    data["pj"] = username
    save_setting(data)
    update.message.reply_text("✅  PJ disimpan")


def del_pj(update, context):
    if update.effective_user.id not in OWNER_IDS or update.effective_chat.type != "private":
        return
    data = load_setting()
    data.pop("pj", None)
    save_setting(data)
    update.message.reply_text("✅  PJ dihapus")


def add_rules(update, context):
    if update.effective_user.id not in OWNER_IDS or update.effective_chat.type != "private":
        return
    text = update.message.reply_to_message.text if update.message.reply_to_message else " ".join(context.args)
    if not text:
        update.message.reply_text("❌  isi rules")
        return
    data = load_setting()
    data["rules"] = text
    save_setting(data)
    update.message.reply_text("✅  rules disimpan")


def del_rules(update, context):
    if update.effective_user.id not in OWNER_IDS or update.effective_chat.type != "private":
        return
    data = load_setting()
    data.pop("rules", None)
    save_setting(data)
    update.message.reply_text("✅  rules dihapus")

def off_cmd(update, context):
    global WORKER_ACTIVE

    if update.effective_user.id not in OWNER_IDS:
        return

    WORKER_ACTIVE = False
    update.message.reply_text("✅ Tagall dimatikan")


def on_cmd(update, context):
    global WORKER_ACTIVE

    if update.effective_user.id not in OWNER_IDS:
        return

    WORKER_ACTIVE = True
    update.message.reply_text("✅ Tagall diaktifkan")

def bc_cmd(update, context):
    if update.effective_user.id not in OWNER_IDS:
        return

    data = load_setting()
    users = data.get("users", [])

    if not users:
        update.message.reply_text("❌ Tidak ada user")
        return

    msg = update.message

    success = 0
    failed = 0

    update.message.reply_text("🚀 Broadcast dimulai...")

    for user_id in users:
        try:
            # 🔥 PRIORITAS: REPLY MESSAGE (ALL TYPE)
            if msg.reply_to_message:
                context.bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=msg.chat_id,
                    message_id=msg.reply_to_message.message_id
                )

            # 🔥 TEXT BIASA
            elif context.args:
                text = " ".join(context.args)
                context.bot.send_message(chat_id=user_id, text=text)

            else:
                continue

            success += 1
            time.sleep(5)  # ⏳ DELAY 5 DETIK

        except:
            failed += 1

    update.message.reply_text(
        f"📢 Broadcast selesai\n\n✅ {success} berhasil\n❌ {failed} gagal"
    )

def start_cmd(update: Update, context: CallbackContext):
    data = load_setting()

    user_id = update.effective_user.id

    users = data.get("users", [])

    if user_id not in users:
        users.append(user_id)
        data["users"] = users
        save_setting(data)

    update.message.reply_text("✅ Bot aktif")

    # ================= LOADING MESSAGE =================
    msg = update.message.reply_text("⚡  Initializing...")

    import time
    import os

    # ================= RGB GLITCH =================
    glitch = [
        "⏩ H ",
        "⏩ H Y ",
        "⏩ H Y P ",
        "⏩ H Y P E ",
        "⏩ H Y P E R ",
        "⏩ H Y P E R I ",
        "⏩ H Y P E R I O ",
        "⏩ H Y P E R I O N ",
]

    for g in glitch:
        time.sleep(0.12)
        try:
            msg.edit_text(g)
        except:
            pass

    # ================= TYPING HACKER =================
    hacker_lines = [
        "⌬ connecting to core...",
        "⌬ bypass firewall...",
        "⌬ injecting payload...",
        "⌬ decrypting system...",
        "⌬ syncing modules..."
    ]

    for line in hacker_lines:
        words = line.split(" ")
        typed = ""

        for w in words:
            typed += w + " "
            try:
                msg.edit_text(typed)
            except:
                pass
            time.sleep(0.03)

        time.sleep(0.05)

    # ================= PROGRESS BAR =================
    for i in range(0, 101, 20):
        bar = "■" * (i // 20) + "□" * (5 - i // 20)
        time.sleep(0.12)
        try:
            msg.edit_text(f"⚡  Booting System...\n[{bar}] {i}%")
        except:
            pass

    # ================= FINAL TEXT (FIX CLEAN) =================
    text = (
    "𓊆 ✨  𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝗕𝗢𝗧 𝗛𝗬𝗣𝗘𝗥𝗜𝗢𝗡  ✨ 𓊇 \n\n"

    "╭───────────────╮\n"
    "│ ٬٬ ࣪ ، 𒀭 sistem tagall otomatis & cepat.\n"
    "│ ٬٬ ࣪ ، 𒀭 Budayakan membaca, biar ga bego!!.\n"
    "│ ٬٬ ࣪ ، 𒀭 jika bingung, silahkan menu user.\n"
    "╰───────────────╯\n\n"

    "✦ 𝐂𝐀𝐑𝐀 𝐏𝐀𝐊𝐀𝐈 ✦\n"
    "⟡ kirim pesan / kata yang ingin ditag\n"
    "⟡ bot auto memproses tagall anda\n"
    "⟡ jika bot diem tidak memberi notip jalan silahkan ke live chat\n\n"

    "        ㅤ\n"
    "     ˖ ╲ ( II.᯽ request & rules partner klik tombol di bawah)"
)
    
    # ================= BUTTON =================
    buttons = []

    if "pj" in data:
        buttons.append([
            InlineKeyboardButton(
                "📩 ✧ 𝑅𝐸𝒬𝒰𝐸𝒮𝒯 𝒫𝒜𝑅𝒯𝒩𝐸𝑅 ✧",
                url=f"https://t.me/{data['pj']}"
            )
        ])

    if "rules" in data:
        buttons.append([
            InlineKeyboardButton(
                "📜 ༺ 𝑹𝑼𝑳𝑬𝑺 𝑷𝑨𝑹𝑻𝑵𝑬𝑹 ༻",
                callback_data="rules"
            )
        ])

    # 🔥 TAMBAHAN LIVE CHAT (EMOJI)
    if data.get("livechat"):
        buttons.append([
            InlineKeyboardButton(
                "💬 ✧ 𝐋𝐈𝐕𝐄 𝐂𝐇𝐀𝐓 ✧",
                url=data["livechat"]
            )
        ])

    markup = InlineKeyboardMarkup(buttons) if buttons else None

    time.sleep(0.2)

    try:
        msg.delete()
    except BaseException:
        pass

    # ================= FOTO SYSTEM =================
    photo_path = "database0/start.jpg"

    if data.get("start_pict"):
        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=data["start_pict"],
            caption=text,
            reply_markup=markup,
            parse_mode="Markdown"
        )

    elif os.path.exists(photo_path):
        with open(photo_path, "rb") as p:
            context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=p,
                caption=text,
                reply_markup=markup,
                parse_mode="Markdown"
            )

# ================= CALLBACK =================
def button_handler(update: Update, context: CallbackContext):
    global WORKER_ACTIVE  # 🔥 WAJIB DI ATAS

    query = update.callback_query
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    try:
        query.answer()
    except:
        pass

    data = load_setting()

    # ================= RULES =================
    if query.data == "rules":
        query.message.reply_text(data.get("rules", "tidak ada rules"))
        return

    # ================= CEK JOIN =================
    if query.data == "cek_join":
        if is_user_joined(user_id):
            query.message.edit_text("✅ Sudah join, kirim ulang perintah")
        else:
            query.answer("JOIN DULU WOI 😡", show_alert=True)
        return

    # ================= STOP MANUAL =================
    if query.data == "manual_stop":
        try:
            member = context.bot.get_chat_member(chat_id, user_id)
            if member.status not in ["administrator", "creator"]:
                query.answer("❌ Khusus admin", show_alert=True)
                return
        except:
            return

        stop_flag[chat_id] = True
        manual_setup.pop(chat_id, None)
        return

    # ================= CLEAR CHAT =================
    if query.data == "manual_clear":
        try:
            member = context.bot.get_chat_member(chat_id, user_id)
            if member.status not in ["administrator", "creator"]:
                query.answer("❌ Khusus admin", show_alert=True)
                return
        except:
            return

        msgs = manual_messages.get(chat_id, [])

        for msg_id in msgs:
            try:
                context.bot.delete_message(chat_id, msg_id)
            except:
                pass

        manual_messages[chat_id] = []
        return

    # ================= DURASI =================
    if query.data.startswith("dur_"):
        handle_durasi(update, context)
        return

    # ================= AUTO TAG BUTTON =================
    elif query.data == "cmd_autotag":
        context.bot.send_message(
            chat_id=query.from_user.id,
            text=(
                "🤖 AUTO TAG SETTING\n\n"
                "Gunakan di private chat:\n"
                "/autotag pesan\n\n"
                "Contoh:\n/autotag WOY LINK GACOR"
            )
        )
        return

    # ================= OWNER BUTTON =================

    elif query.data == "cmd_addpict":
        context.bot.send_message(
            chat_id=query.from_user.id,
            text="🖼️ Reply foto lalu ketik /addpict"
        )

    elif query.data == "cmd_delpict":
        if query.from_user.id not in OWNER_IDS:
            return

        data = load_setting()
        if "start_pict" not in data:
            context.bot.send_message(
                chat_id=query.from_user.id,
                text="⚠️ Foto belum ada"
            )
            return

        data.pop("start_pict", None)
        save_setting(data)

        context.bot.send_message(
            chat_id=query.from_user.id,
            text="✅ Foto berhasil dihapus"
        )

    elif query.data == "cmd_addpj":
        context.bot.send_message(
            chat_id=query.from_user.id,
            text="👤 Kirim: /addpj @username"
        )

    elif query.data == "cmd_delpj":
        if query.from_user.id not in OWNER_IDS:
            return

        data = load_setting()

        if "pj" not in data:
            context.bot.send_message(
                chat_id=query.from_user.id,
                text="⚠️ PJ belum ada"
            )
            return

        data.pop("pj", None)
        save_setting(data)

        context.bot.send_message(
            chat_id=query.from_user.id,
            text="✅ PJ berhasil dihapus"
        )

    elif query.data == "cmd_listpartner":
        if query.from_user.id not in OWNER_IDS:
            return

        data_partner = load_partner()

        if not data_partner:
            context.bot.send_message(
                chat_id=query.from_user.id,
                text="❌ Partner kosong"
            )
            return

        text = "📋 𝐋𝐈𝐒𝐓 𝐏𝐀𝐑𝐓𝐍𝐄𝐑\n\n"

        for i, p in enumerate(data_partner, 1):
            text += f"〔{i}〕 {p['name']}\n"
            text += f"🔗 {p['link']}\n\n"

        context.bot.send_message(
            chat_id=query.from_user.id,
            text=text
        )

    elif query.data == "cmd_on":
        if query.from_user.id not in OWNER_IDS:
            return

        WORKER_ACTIVE = True

        context.bot.send_message(
            chat_id=query.from_user.id,
            text="🟢 Tagall berhasil diaktifkan"
        )

    elif query.data == "cmd_off":
        if query.from_user.id not in OWNER_IDS:
            return

        WORKER_ACTIVE = False

        context.bot.send_message(
            chat_id=query.from_user.id,
            text="🔴 Tagall berhasil dimatikan"
        )

    # ================= BROADCAST =================
    elif query.data == "cmd_bc":
        if query.from_user.id not in OWNER_IDS:
            return

        context.bot.send_message(
            chat_id=query.from_user.id,
            text="📢 Kirim broadcast pakai:\n/bc pesan"
        )
     
# ================= TELETHON =================


async def scrape(chat_id):
    users = {}
    try:
        dialogs = await client.get_dialogs()
        entity = None
        for d in dialogs:
            if d.id == chat_id:
                entity = d.entity
                break
        if not entity:
            print("❌  entity ga ketemu")
            return {}
        async for u in client.iter_participants(entity):
            if not u.bot and u.first_name:
                users[str(u.id)] = u.first_name
    except Exception as e:
        print("❌  scrape error:", e)
    return users

# ================= MEMBER =================
def get_members(chat_id):
    merged = {}
    try:
        r = requests.get(f"{API_URL}?chat_id={chat_id}", timeout=5)
        api_data = r.json()
    except BaseException:
        api_data = {}

    try:
        live_data = loop.run_until_complete(scrape(chat_id))
    except BaseException:
        live_data = {}

    for uid, name in api_data.items():
        merged[str(uid)] = name

    for uid, name in live_data.items():
        merged[str(uid)] = name

    return merged


# ================= LIMIT GC =================
LIMIT_FILE = "limit_gc.json0"

from datetime import datetime, timedelta, timezone

WIB = timezone(timedelta(hours=7))


def get_today_wib():
    return datetime.now(WIB).strftime("%Y-%m-%d")


def load_limit():
    try:
        with open(LIMIT_FILE, "r") as f:
            return json.load(f)
    except:
        return {}


def save_limit(data):
    with open(LIMIT_FILE, "w") as f:
        json.dump(data, f)


# 🔥 WORKER SWITCH (ON / OFF)
WORKER_ACTIVE = True


# 🔥 AUTO RESET LIMIT (00:00 WIB)
def reset_limit_daily():
    while True:
        try:
            now = datetime.now(WIB)

            tomorrow = (now + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            wait_time = (tomorrow - now).total_seconds()

            print(f"⏳ RESET LIMIT DALAM {int(wait_time)} DETIK")

            time.sleep(wait_time)

            save_limit({})
            print("🔥 LIMIT GC DI RESET (00:00 WIB)")

        except Exception as e:
            print("❌ ERROR RESET LIMIT:", e)
            time.sleep(60)


# ================= TAGALL =================
task_queue = Queue()
running_task = False
user_queue = []
progress_map = {}

print("QUEUE INIT:", user_queue)


# ================= PROGRESS REAL =================
def update_progress(user_id, current, total):
    percent = int((current / total) * 100) if total else 0
    bar = "█" * (percent // 10) + "░" * (10 - percent // 10)
    try:
        if user_id in progress_map:
            bot.edit_message_text(
                chat_id=user_id,
                message_id=progress_map[user_id]["msg_id"],
                text=f"🚀 𝐓𝐀𝐆𝐀𝐋𝐋 𝐏𝐑𝐎𝐒𝐄𝐒\n\n[{bar}] {percent}%\n👥 {current}/{total}"
            )
    except BaseException:
        pass

def start_progress(user_id):
    msg = bot.send_message(
        chat_id=user_id,
        text="🚀 𝐓𝐀𝐆𝐀𝐋𝐋 𝐃𝐈𝐌𝐔𝐋𝐀𝐈\n\n⏳    0%"
    )
    progress_map[user_id] = {
        "msg_id": msg.message_id
    }


# ================= AUTO DELETE =================
def auto_delete_messages(chat_id, message_ids):
    print("🧹 AUTO DELETE START")
    time.sleep(120)
    for msg_id in message_ids:
        if not msg_id:
            continue
        try:
            bot.delete_message(chat_id, msg_id)
            print("✔ hapus:", msg_id)
            time.sleep(0.3)
        except Exception as e:
            print("❌   GAGAL HAPUS:", msg_id, e)
    print("✅   AUTO DELETE SELESAI")

            
 # ================= WORKER =================
def tagall_worker():
    global running_task
    print("🔥 WORKER HIDUP")

    while True:
        chat_id, text, user_id = task_queue.get()

        # ================= WORKER OFF =================
        if not WORKER_ACTIVE:
            try:
                bot.send_message(
                    user_id,
                    "❌ Maaf lagi close tagall dulu"
                )
            except:
                pass

            task_queue.task_done()
            continue

        # ================= LIMIT GC =================
        limit_data = load_limit()
        today = get_today_wib()

        links = re.findall(r"(https?://t\.me/\S+)", text)
        partner_link = links[0] if links else "-"
        partner_key = normalize_link(partner_link)

        if limit_data.get(partner_key) == today:
            task_queue.task_done()
            continue

        print("🔥 AMBIL TASK:", user_id)

        try:
            # 🔥 FIX ANTRIAN
            if user_queue and user_queue[0] != user_id:
                time.sleep(0.3)
                task_queue.task_done()
                continue

            running_task = True
            print("🚀 PROSES USER:", user_id)

            start_msg = (
                "🚀 𝐓𝐀𝐆𝐀𝐋𝐋 𝐃𝐈𝐌𝐔𝐋𝐀𝐈\n\n"
                f"🔗 partner : {partner_link}\n"
                "⏰ durasi : 5 menit\n"
                "📍 JIKA BOT EROR SILAHKAN KESINI @livechtBot"
            )

            keyboard_start = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 My Store", url="https://t.me/storegarf")]
            ])

            bot.send_message(chat_id, start_msg)
            bot.send_message(user_id, start_msg, reply_markup=keyboard_start)

            # ================= START =================
            start_progress(user_id)
            sent_messages = []
            sent = 0

            members = get_members(chat_id)
            if not members:
                task_queue.task_done()
                continue

            user_ids = list(members.keys())
            total = len(user_ids)

            random.shuffle(user_ids)

            BATCH_SIZE = 4
            BASE_DELAY = 1.4
            start_time = time.time()
            duration = 300

            last_success_time = time.time()

            # ================= LOOP TAG =================
            while time.time() - start_time < duration:

                if time.time() - last_success_time > 15:
                    print("⚠️ STUCK DETECTED, RESTART LOOP")
                    break

                for i in range(0, total, BATCH_SIZE):
                    if time.time() - start_time >= duration:
                        break

                    batch = user_ids[i:i + BATCH_SIZE]

                    mention_text = ""
                    for uid in batch:
                        name = html.escape(members[uid])
                        mention_text += f'<a href="tg://user?id={uid}">{name}</a> '

                    retry = 0

                    while retry < 3:
                        try:
                            msg = bot.send_message(
                                chat_id,
                                f" 💕 𝑩𝑶𝑻 𝑻𝑨𝑮𝑨𝑳𝑳 𝐇𝐘𝐏𝐄𝐑𝐈𝐎𝐍 💖\n\n{text}\n\n{mention_text}",
                                parse_mode="HTML",
                                timeout=10
                            )

                            if msg and msg.message_id:
                                sent_messages.append(msg.message_id)

                            sent += len(batch)
                            update_progress(user_id, sent, total)

                            last_success_time = time.time()

                            print(f"📊 PROGRESS: {sent}/{total}")
                            break

                        except Exception as e:
                            print("❌       ", e)
                            retry += 1

                            if "Retry in" in str(e):
                                try:
                                    wait = int(re.search(r"Retry in (\d+)", str(e)).group(1))
                                    print(f"⏳ RETRY WAIT: {wait}s")
                                    time.sleep(wait + 1)
                                except:
                                    time.sleep(3)

                            elif "Too Many Requests" in str(e):
                                print("🚫 FLOOD DETECTED")
                                time.sleep(3 + retry)

                            elif "Timed out" in str(e):
                                print("⌛ TIMEOUT DETECTED")
                                time.sleep(2 + retry)

                            else:
                                time.sleep(1 + retry)

                    time.sleep(BASE_DELAY + random.uniform(0.15, 0.35))

            # ================= SELESAI =================
            keyboard_done = InlineKeyboardMarkup([
                [InlineKeyboardButton("👑 Creator", url="https://t.me/Brsik23")]
            ])

            bot.send_message(
                chat_id,
                f"✅     𝐓𝐀𝐆𝐀𝐋𝐋 𝐒𝐄𝐋𝐄𝐒𝐀𝐈\n\n"
                f"🔗 partner : {partner_link}\n"
                f"👥 Total: {sent}",
                reply_markup=keyboard_done
            )

            # SAVE LIMIT
            limit_data[partner_key] = today
            save_limit(limit_data)

            print("📦 TOTAL MSG:", len(sent_messages))
            print("🧾 SAMPLE MSG ID:", sent_messages[:5])

            # AUTO DELETE
            if sent_messages:
                threading.Thread(
                    target=auto_delete_messages,
                    args=(chat_id, sent_messages.copy()),
                    daemon=True
                ).start()

            # PRIVATE
            try:
                if user_id in progress_map:
                    keyboard_private_done = InlineKeyboardMarkup([
                        [InlineKeyboardButton("👑 Creator", url="https://t.me/Brsik23")]
                    ])

                    bot.edit_message_text(
                        chat_id=user_id,
                        message_id=progress_map[user_id]["msg_id"],
                        text=f"✅  𝐓𝐀𝐆𝐀𝐋𝐋 𝐒𝐄𝐋𝐀𝐈\n\n"
                             f"🔗 partner : {partner_link}\n"
                             f"🧹 auto delete aktif\n"
                             f"👥 Total: {sent}\n"
                             f"⏱ 5 menit",
                        reply_markup=keyboard_private_done
                    )
            except Exception as e:
                print("❌  edit private:", e)

        except Exception as e:
            print("❌  ERROR:", e)

        finally:
            running_task = False

            # 🔥 HAPUS ANTRIAN (SUDAH DIGABUNG DI SINI)
            if user_queue:
                if user_queue[0] == user_id:
                    user_queue.pop(0)
                elif user_id in user_queue:
                    user_queue.remove(user_id)

            task_queue.task_done()


# 🔥 AUTO RESET
threading.Thread(target=reset_limit_daily, daemon=True).start()                               


# ================= CEK JOIN =================
def is_user_joined(user_id):
    try:
        member = bot.get_chat_member(FORCE_GROUP, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ================= HANDLER =================
def handle_private(update: Update, context: CallbackContext):
    global running_task

    if not update.message:
        return

    msg = update.message

    if msg.chat.type != "private":
        return

    user_id = update.effective_user.id

    # ================= FORCE JOIN =================
    if not is_user_joined(user_id):
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 JOIN GROUP", url=FORCE_LINK)],
            [InlineKeyboardButton("✅ CEK LAGI", callback_data="cek_join")]
        ])

        msg.reply_text(
            "🚫 AKSES DITOLAK\n\n"
            "📢 Kamu wajib join group dulu!\n"
            "🔓 Setelah join klik CEK LAGI",
            reply_markup=buttons
        )
        return

    # ================= LANJUT =================
    text = msg.text or ""

    # ================= FILTER AWAL =================

    if not WORKER_ACTIVE:
        msg.reply_text("❌ Maaf, tagall sedang OFF")
        return

    if not text:
        return

    # ================= VALIDASI LINK =================
    links = re.findall(r"(https?://t\.me/\S+)", text)

    if not links:
        msg.reply_text("❌ Tidak ada link t.me")
        return

    data = load_partner()

    # 🔥 FIX VALIDASI (AMAN + SUPPORT PRIVATE & PUBLIC)
    valid = any(
        isinstance(p, dict) and (
            normalize_link(l) == p.get("username") or
            l in p.get("link", "")
        )
        for l in links for p in data
    )

    if not valid:
        msg.reply_text("❌ Link tidak terdaftar partner")
        return

    # ================= CEK LIMIT =================
    limit_data = load_limit()
    today = get_today_wib()

    partner_link = links[0]

    # 🔥 FIX KEY (AMAN UNTUK PRIVATE & PUBLIC)
    partner_key = next(
        (
            p.get("username")
            for p in data
            if partner_link in p.get("link", "")
        ),
        normalize_link(partner_link)
    )

    if limit_data.get(partner_key) == today:
        msg.reply_text("❌ Group ini sudah request tagall hari ini")
        return

    # ================= LIMIT ANTRIAN =================
    antrian = task_queue.qsize()

    if antrian >= 5:
        msg.reply_text(
            "⚠️ 𝐀𝐍𝐓𝐑𝐈𝐀𝐍 𝐏𝐄𝐍𝐔𝐇\n\n"
            "⏳ Tunggu beberapa menit\n"
            "🚀 Bot sedang sibuk"
        )
        return

    user_id = msg.from_user.id

    # ================= MASUK ANTRIAN =================
    if user_id not in user_queue:
        user_queue.append(user_id)

    posisi = user_queue.index(user_id) + 1

    # ================= NOTIF PRIVATE =================
    if posisi == 1 and not running_task:
        msg.reply_text(
            "📢 Permintaan kamu sedang di proses\n"
            "⏳ Durasi: 5 menit\n"
            "💾 cukup forward pesan ini saja\n\n"
            "✨ Tunggu sampai selesai ya..."
        )
    else:
        msg.reply_text(
            f"⏳ 𝐌𝐀𝐒𝐔𝐊 𝐀𝐍𝐓𝐑𝐈𝐀𝐍\n\n"
            f"📊 Posisi kamu: {posisi}\n"
            f"🚀 Akan diproses setelah yang lain selesai"
        )

    # ================= MASUK TASK =================
    for chat_id in TARGET_CHATS:
        task_queue.put((chat_id, text, user_id))

    # ================= START WORKER =================
    if not running_task:
        threading.Thread(target=tagall_worker, daemon=True).start()


DEBUG_MODE = True
VENV_PYTHON = "/root/hyperionn/venv/bin/python"
BOT_FILE = "/root/hyperionn/bot0.py"

LAST_BACKUP = None


# ================= DEBUG =================
def debug_log(msg):
    if DEBUG_MODE:
        print(f"[DEBUG] {msg}")


# ================= CORE FILES =================
CORE_FILES = [
    "setting.json0",
    "partner.json0",
    "buttons.json0",
    "autotag.json0"
]


# ================= ROLLBACK =================
def rollback_last_backup(update):
    global LAST_BACKUP

    if not LAST_BACKUP or not os.path.exists(LAST_BACKUP):
        update.message.reply_text("❌ tidak ada backup")
        return

    try:
        update.message.reply_text("🔁 rollback...")

        for f in CORE_FILES:
            if os.path.exists(f):
                os.remove(f)

        if os.path.exists("database0"):
            shutil.rmtree("database0")

        with zipfile.ZipFile(LAST_BACKUP, 'r') as z:
            z.extractall()

        update.message.reply_text("✅ rollback sukses")

    except Exception as e:
        update.message.reply_text(f"❌ rollback gagal: {e}")


# ================= RESTORE =================
def restore_cmd(update, context):
    global LAST_BACKUP

    user_id = update.effective_user.id

    if user_id not in OWNER_IDS:
        update.message.reply_text("❌ bukan owner")
        return

    if not update.message.reply_to_message or not update.message.reply_to_message.document:
        update.message.reply_text("❌ reply file zip")
        return

    try:
        update.message.reply_text("⏳ restore...")

        file = update.message.reply_to_message.document.get_file()
        file.download("restore.zip")

        if not zipfile.is_zipfile("restore.zip"):
            update.message.reply_text("❌ zip rusak")
            return

        with zipfile.ZipFile("restore.zip", 'r') as z:
            files = z.namelist()
            debug_log(files)

            if not any(f in files for f in CORE_FILES):
                update.message.reply_text("❌ struktur salah")
                return

            # ================= BACKUP BEFORE RESTORE =================
            LAST_BACKUP = f"backup_before_restore_{int(time.time())}.zip"

            with zipfile.ZipFile(LAST_BACKUP, 'w', zipfile.ZIP_DEFLATED) as backup:
                for f in CORE_FILES:
                    if os.path.exists(f):
                        backup.write(f)

                if os.path.exists("database0"):
                    for root, _, files2 in os.walk("database0"):
                        for f in files2:
                            backup.write(os.path.join(root, f))

            # ================= CLEAN =================
            for f in CORE_FILES:
                if os.path.exists(f):
                    os.remove(f)

            if os.path.exists("database0"):
                shutil.rmtree("database0")

            # ================= EXTRACT =================
            z.extractall()

        update.message.reply_text("✅ restore sukses")

        # ================= VENV RESTART =================
        os.execv(VENV_PYTHON, ["python", BOT_FILE])

    except Exception as e:
        debug_log(e)
        update.message.reply_text(f"❌ restore gagal: {e}")
        

# ================= MAIN =================

def main():
    global bot

    updater = Updater(
        TOKEN,
        use_context=True,
        request_kwargs={
            'read_timeout': 20,
            'connect_timeout': 20
        }
    )

    bot = updater.bot

    # 🔥 LOAD AUTO TAG DATA
    load_autotag()

    # 🔥 DATABASE
    database0.start_database_system(bot)

    dp = updater.dispatcher

    register_menu(dp)
    register_rekab (dp)
    register_fitur(dp)
    register_absen(dp)
    # ================= COMMAND =================
    dp.add_handler(CommandHandler("restore", restore_cmd))
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("help", help_owner))
    dp.add_handler(CommandHandler("addlivechat", add_livechat))
    dp.add_handler(CommandHandler("dellivechat", del_livechat))
    dp.add_handler(CommandHandler("addpartner", add_partner))
    dp.add_handler(CommandHandler("delpartner", del_partner))
    dp.add_handler(CommandHandler("listpartner", list_partner))
    dp.add_handler(CommandHandler("addpict", add_pict))
    dp.add_handler(CommandHandler("delpict", del_pict))
    dp.add_handler(CommandHandler("addpj", add_pj))
    dp.add_handler(CommandHandler("delpj", del_pj))
    dp.add_handler(CommandHandler("addrules", add_rules))
    dp.add_handler(CommandHandler("delrules", del_rules))
    dp.add_handler(CommandHandler("off", off_cmd))
    dp.add_handler(CommandHandler("on", on_cmd))
    dp.add_handler(CommandHandler("bc", bc_cmd))
    dp.add_handler(CallbackQueryHandler(partner_callback, pattern="^partner_"))
    dp.add_handler(
    CallbackQueryHandler(partner_callback, pattern="^(partner_|edit_)")
)
    # 🔥 TAGALL (MANUAL)
    dp.add_handler(CommandHandler("tagall", tagall_cmd))
    dp.add_handler(CommandHandler("cancel", cancel_cmd)) 
    dp.add_handler(CommandHandler("addbuttontag", addbuttontag_cmd))

    # 🔥 AUTO TAG (PRIVATE ONLY)
    dp.add_handler(CommandHandler("autotag", autotag_menu))
    dp.add_handler(CommandHandler("clearauto", clearauto))
    dp.add_handler(CommandHandler("onauto", onauto))
    dp.add_handler(CommandHandler("offauto", offauto))
    # ================= CALLBACK =================
    # 🔥 MANUAL TAG (WAJIB PALING ATAS)
    dp.add_handler(CallbackQueryHandler(handle_durasi, pattern="^dur_"))

    # 🔥 AUTO TAG (WAJIB DI ATAS button_handler)
    dp.add_handler(CallbackQueryHandler(pilih_jam, pattern="^setjam_"))
    dp.add_handler(CallbackQueryHandler(pilih_durasi, pattern="^autodur_"))

    # 🔥 tombol lain
    dp.add_handler(CallbackQueryHandler(button_handler))

    # ================= PRIVATE =================
    dp.add_handler(
        MessageHandler(
            Filters.text & Filters.private & ~Filters.command,
            handle_private
        )
    )

    # ================= TELETHON =================
    client.start()
    print("✅ Telethon nyala")

    # ================= WORKER =================
    worker_thread = threading.Thread(target=tagall_worker)
    worker_thread.daemon = True
    worker_thread.start()
    print("🔥 WORKER STARTED")

    # ================= AUTO TAG WORKER =================
    auto_thread = threading.Thread(
        target=auto_tag_worker,
        args=(updater.bot,),
        daemon=True
    )
    auto_thread.start()
    print("⏰ AUTO TAG WORKER STARTED")

    # ================= AUTO RESET LIMIT =================
    reset_thread = threading.Thread(target=reset_limit_daily)
    reset_thread.daemon = True
    reset_thread.start()

    # ================= START BOT =================
    updater.start_polling(
        poll_interval=2.3,
        timeout=20,
        clean=True
    )

    print("🚀 BOT RUNNING...")
    updater.idle()


# ================= RUN =================
if __name__ == "__main__":
    main()
