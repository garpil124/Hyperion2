from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import sqlite3
import datetime

# ================= DB =================

db = sqlite3.connect("tmo.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS jobdast(
    group_id INTEGER PRIMARY KEY,
    host TEXT,
    backup TEXT,
    keliling TEXT,
    tagall TEXT,
    gcast TEXT,
    link TEXT
)
""")
db.commit()

panel_msg = {}
user_state = {}
last_input = {}

FIELDS_USER = ["host", "backup", "keliling"]
FIELDS_TEXT = ["tagall", "gcast", "link"]
ALL_FIELDS = FIELDS_USER + FIELDS_TEXT


# ================= INIT =================

def init_group(gid):
    cur.execute("INSERT OR IGNORE INTO jobdast(group_id) VALUES(?)", (gid,))
    db.commit()


# ================= GET DATA =================

def get_data(gid):
    init_group(gid)
    cur.execute("""
        SELECT host,backup,keliling,tagall,gcast,link
        FROM jobdast WHERE group_id=?
    """, (gid,))
    return cur.fetchone() or ("", "", "", "", "", "")


def get_field(gid, f):
    cur.execute(f"SELECT {f} FROM jobdast WHERE group_id=?", (gid,))
    r = cur.fetchone()
    return r[0] if r else ""


# ================= FORMAT =================

def nice_date():
    return datetime.datetime.now().strftime("%d/%m/%Y")


def format_text(x):
    if not x:
        return "-"
    return "\n".join([i for i in x.split("\n") if i.strip()])


def format_user(x):
    if not x:
        return "-"
    out = []
    for v in x.split("\n"):
        try:
            uid, name = v.split("|", 1)
            out.append(f"• {name}")
        except:
            out.append(v)
    return "\n".join(out)


def build_panel(gid):
    h,b,k,t,g,l = get_data(gid)

    return f"""
✦ JOBDAST PANEL ✦
📅 {nice_date()}

◆ HOST :
{format_user(h)}

◆ BACKUP :
{format_user(b)}

◆ KELILING :
{format_user(k)}

◆ TAGALL :
{format_text(t)}

◆ GCAST :
{format_text(g)}

◆ LINK :
{format_text(l)}

🛍 @storegarf
"""


# ================= KEYBOARD =================

def panel_btn():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("HOST", callback_data="jobdast:host"),
         InlineKeyboardButton("DEL", callback_data="jobdast:reset_host")],

        [InlineKeyboardButton("BACKUP", callback_data="jobdast:backup"),
         InlineKeyboardButton("DEL", callback_data="jobdast:reset_backup")],

        [InlineKeyboardButton("KELILING", callback_data="jobdast:keliling"),
         InlineKeyboardButton("DEL", callback_data="jobdast:reset_keliling")],

        [InlineKeyboardButton("TAGALL", callback_data="jobdast:tagall"),
         InlineKeyboardButton("GCAST", callback_data="jobdast:gcast")],

        [InlineKeyboardButton("LINK", callback_data="jobdast:link")],

        [InlineKeyboardButton("COPY ALL", callback_data="jobdast:copy_all"),
         InlineKeyboardButton("RESET ALL", callback_data="jobdast:reset_all")]
    ])


# ================= COMMAND =================

def getjobdast_cmd(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    init_group(chat_id)

    msg = update.message.reply_text(
        build_panel(chat_id),
        reply_markup=panel_btn()
    )

    panel_msg[chat_id] = msg.message_id


# ================= CALLBACK =================

def jobdast_cb(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    chat_id = query.message.chat.id
    user_id = query.from_user.id

    data = query.data.replace("jobdast:", "")

    # ===== ADD USER FIELD =====
    if data in FIELDS_USER:
        old = get_field(chat_id, data)
        new = old + f"\n{user_id}|{query.from_user.first_name}"

        cur.execute(f"UPDATE jobdast SET {data}=? WHERE group_id=?", (new, chat_id))
        db.commit()

        return query.edit_message_text(build_panel(chat_id), reply_markup=panel_btn())


    # ===== TEXT INPUT MODE =====
    if data in FIELDS_TEXT:
        user_state[user_id] = (chat_id, data)
        return query.message.reply_text("Kirim teks ke bot...")


    # ===== RESET ALL =====
    if data == "reset_all":
        cur.execute("""
            UPDATE jobdast SET host='',backup='',keliling='',
            tagall='',gcast='',link=''
            WHERE group_id=?
        """, (chat_id,))
        db.commit()

        return query.edit_message_text(build_panel(chat_id), reply_markup=panel_btn())


    # ===== COPY =====
    if data == "copy_all":
        return query.message.reply_text(build_panel(chat_id))


# ================= TEXT HANDLER =================

def text_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_state:
        return

    chat_id, field = user_state[user_id]

    old = get_field(chat_id, field)
    new = old + "\n" + text

    cur.execute(f"UPDATE jobdast SET {field}=? WHERE group_id=?", (new, chat_id))
    db.commit()

    del user_state[user_id]

    update.message.reply_text("SAVED ✅")

    # refresh panel
    if chat_id in panel_msg:
        try:
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=panel_msg[chat_id],
                text=build_panel(chat_id),
                reply_markup=panel_btn()
            )
        except:
            pass


# ================= REGISTER =================

def register_jobdast(dp):
    dp.add_handler(CommandHandler("getjobdast", getjobdast_cmd))
    dp.add_handler(CallbackQueryHandler(jobdast_cb, pattern="jobdast:"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_handler))
