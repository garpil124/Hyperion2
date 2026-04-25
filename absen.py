  # ================= ABSEN BOT SYSTEM (FULL AUTO FINAL) =================

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from datetime import datetime, time
import pytz
import sqlite3
import pesan

WIB = pytz.timezone("Asia/Jakarta")

# ================= DB =================

db = sqlite3.connect("absen.db9", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS absen (
    chat_id INTEGER,
    user_id INTEGER,
    name TEXT,
    type TEXT,
    alasan TEXT,
    date TEXT,
    time TEXT
)
""")
db.commit()

# ================= MEMORY =================

absen_msg = {}
pending_izin = {}

last_day = None  # 🔥 penting biar bisa detect reset


# ================= SAVE =================

def save_absen(chat_id, user_id, name, tipe, alasan=None):
    now = datetime.now(WIB)

    cur.execute("""
        INSERT INTO absen (chat_id, user_id, name, type, alasan, date, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        chat_id,
        user_id,
        name,
        tipe,
        alasan,
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M")
    ))
    db.commit()


# ================= LOAD =================

def load_absen(chat_id):
    cur.execute(
        "SELECT name, type, alasan, time FROM absen WHERE chat_id=?",
        (chat_id,)
    )
    rows = cur.fetchall()

    data = {"hadir": [], "izin": [], "sakit": []}

    for name, tipe, alasan, time in rows:
        if tipe == "hadir":
            data["hadir"].append((name, time))
        elif tipe == "izin":
            data["izin"].append((name, alasan, time))
        elif tipe == "sakit":
            data["sakit"].append((name, time))

    return data


# ================= FORMAT =================

def format_absen(chat_id):
    data = load_absen(chat_id)
    now = datetime.now(WIB)

    total = len(data["hadir"]) + len(data["izin"]) + len(data["sakit"])
    motivasi = pesan.get_quote()

    text = f"""
╔════════════════════════════════════╗
            ✦ 𝘼𝘽𝙎𝙀𝙉 𝙃𝘼𝙍𝙄𝘼𝙉 ✦
╚════════════════════════════════════╝

📅 {now.strftime('%A, %d %B %Y')}
⏰ {now.strftime('%H:%M WIB')}

────────────────────────────────────

🟢 HADIR : {len(data['hadir'])}
🟡 IZIN  : {len(data['izin'])}
🔴 SAKIT : {len(data['sakit'])}
👥 TOTAL : {total}

────────────────────────────────────
"""

    for n, t in data["hadir"]:
        text += f"\n🟢 {n} ⏰ {t}"

    for n, a, t in data["izin"]:
        text += f"\n🟡 {n} ⏰ {t}\n   └ {a}"

    for n, t in data["sakit"]:
        text += f"\n🔴 {n} ⏰ {t}"

    if total == 0:
        text += "\n\n⚠️ Belum ada absen"

    text += f"\n\n────────────────────────────────────\n💬 “{motivasi}”"

    return text


# ================= KEYBOARD =================

def get_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟢 HADIR", callback_data="absen_hadir"),
            InlineKeyboardButton("🟡 IZIN", callback_data="absen_izin"),
            InlineKeyboardButton("🔴 SAKIT", callback_data="absen_sakit"),
        ]
    ])


# ================= PIN =================

def safe_pin(context, chat_id, msg_id):
    try:
        context.bot.unpin_chat_message(chat_id)
    except:
        pass

    try:
        context.bot.pin_chat_message(chat_id, msg_id, disable_notification=True)
    except:
        pass


# ================= DAILY RESET AUTO =================

def daily_reset(context):
    global last_day

    today = datetime.now(WIB).strftime("%Y-%m-%d")

    if last_day == today:
        return

    chats = cur.execute("SELECT DISTINCT chat_id FROM absen").fetchall()

    for (chat_id,) in chats:
        try:
            # ✅ kirim rekap
            context.bot.send_message(
                chat_id,
                "📊 DAILY REKAP\n\n" + format_absen(chat_id)
            )

            # ✅ hapus data
            cur.execute("DELETE FROM absen WHERE chat_id=?", (chat_id,))
            db.commit()

            # ✅ kirim panel baru
            msg = context.bot.send_message(
                chat_id,
                format_absen(chat_id),
                reply_markup=get_keyboard()
            )

            # ✅ pin
            absen_msg[chat_id] = msg.message_id
            safe_pin(context, chat_id, msg.message_id)

        except Exception as e:
            print("RESET ERROR:", e)

    last_day = today


# ================= COMMAND =================

def absen_cmd(update, context):
    daily_reset(context)

    chat_id = update.effective_chat.id

    msg = update.message.reply_text(
        format_absen(chat_id),
        reply_markup=get_keyboard()
    )

    absen_msg[chat_id] = msg.message_id
    safe_pin(context, chat_id, msg.message_id)


# ================= CALLBACK =================

def absen_button(update, context):
    daily_reset(context)

    query = update.callback_query
    query.answer()

    user = query.from_user
    chat_id = query.message.chat.id
    tipe = query.data.split("_")[1]

    cur.execute(
        "SELECT 1 FROM absen WHERE chat_id=? AND user_id=?",
        (chat_id, user.id)
    )

    if cur.fetchone():
        return query.answer("❌ Sudah absen", show_alert=True)

    if tipe == "hadir":
        save_absen(chat_id, user.id, user.first_name, "hadir")

    elif tipe == "sakit":
        save_absen(chat_id, user.id, user.first_name, "sakit")

    elif tipe == "izin":
        pending_izin[user.id] = chat_id
        return query.message.reply_text("🟡 Kirim alasan izin:")

    try:
        if chat_id in absen_msg:
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=absen_msg[chat_id],
                text=format_absen(chat_id),
                reply_markup=get_keyboard()
            )
    except:
        pass


# ================= IZIN =================

def izin_handler(update, context):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if pending_izin.get(user.id) != chat_id:
        return

    save_absen(chat_id, user.id, user.first_name, "izin", update.message.text)
    del pending_izin[user.id]

    update.message.reply_text("✅ izin dicatat")


# ================= AUTO CHECK SAAT BOT HIDUP =================

def auto_check(context):
    daily_reset(context)


# ================= REGISTER =================

def register_absen(app):
    app.add_handler(CommandHandler("absen", absen_cmd))
    app.add_handler(CallbackQueryHandler(absen_button, pattern="^absen_"))
    app.add_handler(MessageHandler(Filters.text & ~Filters.command, izin_handler))

    # 🔥 AUTO RESET JAM 00:00 WIB
    app.job_queue.run_daily(
        daily_reset,
        time=time(0, 0, tzinfo=WIB)
    )

    # 🔥 CEK SAAT BOT START (ANTI KELEWAT RESET)
    app.job_queue.run_once(auto_check, 5)  
