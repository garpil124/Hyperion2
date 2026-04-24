import sqlite3
import re
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler

# ======================
# DB
# ======================
db = sqlite3.connect("absen1.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS rekab_tmo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER,
    nama TEXT,
    gc TEXT,
    status TEXT DEFAULT 'MISSING',
    note TEXT DEFAULT ''
)
""")
db.commit()

# ======================
# STATE
# ======================
page_state = {}

# ======================
# GET DATA
# ======================
def get_data(gid):
    cur.execute("""
    SELECT id, nama, gc, status, note
    FROM rekab_tmo
    WHERE group_id=?
    ORDER BY id ASC
    """, (gid,))
    return cur.fetchall()

# ======================
# STATUS ICON
# ======================
def status_icon(status):
    s = status.upper()
    if s == "MISSING":
        return "🟡 MISSING"
    elif s == "DONE":
        return "🟢 DONE"
    elif s == "CLOSED":
        return "🔴 CLOSED"
    return "⚪ UNKNOWN"

# ======================
# BUILD UI
# ======================
def build(gid, page=1):
    data = get_data(gid)

    total_page = max(1, (len(data) + 4) // 5)
    page = max(1, min(page, total_page))

    start = (page - 1) * 5
    rows = data[start:start + 5]

    now = datetime.now()

    text = (
        f"╔══════════════════════╗\n"
        f"      ✦ KELILING TMO ✦\n"
        f"╚══════════════════════╝\n"
        f"📅 {now.strftime('%d-%m-%Y')} | PAGE {page}/{total_page}\n"
        f"══════════════════════\n\n"
    )

    keyboard = []

    if not rows:
        text += "❌ DATA KOSONG\n\n"

    for rid, nama, gc, status, note in rows:
        text += (
            f"🔸 ID     : {rid}\n"
            f"🔹 NAME   : {nama}\n"
            f"🔹 LINK   : {gc}\n"
            f"🔹 STATUS : {status_icon(status)}\n"
            f"══════════════════════\n\n"
        )

        keyboard.append([
            InlineKeyboardButton("🟡", callback_data=f"miss_{rid}"),
            InlineKeyboardButton("🟢", callback_data=f"done_{rid}"),
            InlineKeyboardButton("🔴", callback_data=f"close_{rid}"),
            InlineKeyboardButton("🗑", callback_data=f"del_{rid}")
        ])

    # NAV
    keyboard.append([
        InlineKeyboardButton("⬅️", callback_data="prev"),
        InlineKeyboardButton("➡️", callback_data="next")
    ])

    # ACTION
    keyboard.append([
        InlineKeyboardButton("🔄 REFRESH STATUS", callback_data="reset_status")
    ])

    keyboard.append([
        InlineKeyboardButton("📦 PREVIEW", callback_data="preview_all")
    ])

    keyboard.append([
        InlineKeyboardButton("🧨 CLEAR ALL", callback_data="clear_all")
    ])

    return text, InlineKeyboardMarkup(keyboard), total_page

# ======================
# COMMAND ADD
# ======================
def addrekab(update: Update, context: CallbackContext):
    gid = update.effective_chat.id
    raw = update.message.text.replace("/addrekab", "").strip()

    if not raw:
        update.message.reply_text("❌ kosong")
        return

    count = 0

    for line in raw.split("\n"):
        line = line.strip()
        if not line:
            continue

        match = re.search(r"(https?://t\.me/\S+|@\w+)", line)
        if not match:
            continue

        gc = match.group(1)
        nama = line.replace(gc, "").strip() or "UNKNOWN"

        cur.execute(
            "INSERT INTO rekab_tmo (group_id, nama, gc) VALUES (?,?,?)",
            (gid, nama, gc)
        )
        count += 1

    db.commit()
    update.message.reply_text(f"✅ REKAB MASUK: {count}")

# ======================
# COMMAND SHOW
# ======================
def rekab(update: Update, context: CallbackContext):
    gid = update.effective_chat.id

    text, markup, _ = build(gid, 1)
    msg = update.message.reply_text(text, reply_markup=markup)

    page_state[gid] = {"page": 1, "msg_id": msg.message_id}

# ======================
# CALLBACK
# ======================
def button_cb(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    gid = query.message.chat.id

    try:
        state = page_state.get(gid, {"page": 1})
        page = state.get("page", 1)

        if data.startswith("miss_"):
            rid = int(data.split("_")[1])
            cur.execute("UPDATE rekab_tmo SET status='MISSING' WHERE id=?", (rid,))

        elif data.startswith("done_"):
            rid = int(data.split("_")[1])
            cur.execute("UPDATE rekab_tmo SET status='DONE' WHERE id=?", (rid,))

        elif data.startswith("close_"):
            rid = int(data.split("_")[1])
            cur.execute("UPDATE rekab_tmo SET status='CLOSED' WHERE id=?", (rid,))

        elif data.startswith("del_"):
            rid = int(data.split("_")[1])
            cur.execute("DELETE FROM rekab_tmo WHERE id=?", (rid,))

        elif data == "reset_status":
            cur.execute("UPDATE rekab_tmo SET status='MISSING' WHERE group_id=?", (gid,))
            db.commit()
            query.answer("🔄 STATUS DI RESET", show_alert=False)

        elif data == "clear_all":
            cur.execute("DELETE FROM rekab_tmo WHERE group_id=?", (gid,))
            db.commit()
            query.edit_message_text("🧨 SEMUA REKAB DIHAPUS")
            query.answer("CLEARED ✔️")
            return

        elif data == "preview_all":
            rows = get_data(gid)

            text = f"📦 FULL REKAP\nTOTAL: {len(rows)}\n\n"

            for i, (rid, nama, gc, status, note) in enumerate(rows, 1):
                text += f"{i}. {nama}\n{gc}\n{status_icon(status)}\n\n"

            for chunk in [text[i:i+3500] for i in range(0, len(text), 3500)]:
                context.bot.send_message(gid, chunk)

            return

        elif data == "prev":
            page -= 1

        elif data == "next":
            page += 1

        else:
            return

        db.commit()

        text, markup, total_page = build(gid, page)
        page_state[gid]["page"] = page

        query.edit_message_text(text, reply_markup=markup)
        query.answer("UPDATED ✔️")

    except Exception as e:
        query.answer(f"ERROR: {e}", show_alert=True)

# ======================
# REGISTER
# ======================
def register_rekab(dp):
    dp.add_handler(CommandHandler("addrekab", addrekab))
    dp.add_handler(CommandHandler("rekab", rekab))

    dp.add_handler(CallbackQueryHandler(
        button_cb,
        pattern=r"^(miss_|done_|close_|del_|prev|next|preview_all|clear_all|reset_status)"
    ))
