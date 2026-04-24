from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler
import requests
from io import BytesIO

# ================= MENU COMMAND =================

def menu_cmd(update, context):
    text = """╭━━━━━━━━━━━━━━━━━━━━━━━╮
⚡ 𝗛𝗘𝗟𝗣 & 𝗙𝗜𝗧𝗨𝗥 𝗕𝗢𝗧 ⚡
╰━━━━━━━━━━━━━━━━━━━━━━━╯

👋 𝐒𝐞𝐥𝐚𝐦𝐚𝐭 𝐝𝐚𝐭𝐚𝐧𝐠 𝐝𝐢 𝐛𝐨𝐭 𝐚𝐮𝐭𝐨𝐭𝐚𝐠𝐚𝐥𝐥!

𝐁𝐞𝐫𝐢𝐤𝐮𝐭 𝐩𝐞𝐧𝐣𝐞𝐥𝐚𝐬𝐚𝐧 & 𝐤𝐞𝐠𝐮𝐧𝐚𝐚𝐧 𝐛𝐨𝐭 𝐢𝐧𝐢 👇

━━━━━━━━━━━━━━━━━━━━━━━
🤖 𝗕𝗢𝗧 𝗔𝗨𝗧𝗢 𝗦𝗬𝗦𝗧𝗘𝗠 𝗔𝗖𝗧𝗜𝗩𝗘

⚡ BOT INI AUTOTAGALL PARTNER
➜ Kᴀᴍᴜ ᴄᴜᴋᴜᴘ /sᴛᴀʀᴛ ʙᴏᴛ
➜ Tᴜɴɢɢᴜ ᴘʀᴏsᴇs ʟᴏᴀᴅɪɴɢ ɪɴsᴛᴀʟʟ sʏsᴛᴇᴍ
➜ ᴀɴᴅᴀ ᴄᴜᴋᴜᴘ ᴋɪʀɪᴍ ᴋᴀᴛᴀ ᴋᴀᴛᴀɴʏᴀ sᴀJᴀ, ɪɴɪ sɪsᴛᴇᴍ ᴏᴛᴏᴍᴀᴛɪs
➜ Lᴀʟᴜ ʙᴇʀJᴀʟᴀɴ ᴅɪ ɢʀᴏᴜᴘ

🔥 FITUR AUTO TAGALL:
• Nɢᴇᴛᴀɢ sᴇᴍᴜᴀ ᴍᴇᴍʙᴇʀ ᴏᴛᴏᴍᴀᴛɪs
• Jᴀʟᴀɴ sᴇʟᴀᴍᴀ 𝟻 ᴍᴇɴɪᴛ
• Aᴜᴛᴏ ᴄʟᴇᴀʀ / ʀᴇsᴇᴛ sᴇᴛᴇʟᴀʜ sᴇʟᴇsᴀɪ
• Bɪsᴀ ᴅɪJᴀʟᴀɴᴋᴀɴ ᴜʟᴀɴɢ ᴋᴀᴘᴀɴ sᴀJᴀ

⚠️ CATATAN PARTNER:
• Jɪᴋᴀ ᴘᴀʀᴛɴᴇʀ ʙᴇʟᴜᴍ ᴛᴇʀᴅᴀғᴛᴀʀ, sɪʟᴀᴋᴀɴ ᴀJᴜᴋᴀɴ ʀᴇǫᴜᴇsᴛ
• Hᴀʀᴀᴘ ᴋᴏɴғɪʀᴍᴀsɪ Jɪᴋᴀ ᴀᴅᴀ ᴘᴇʀɢᴀɴᴛɪᴀɴ ʟɪɴᴋ ɢʀᴏᴜᴘ!!
• Bᴏᴛ ʜᴀɴʏᴀ ᴜɴᴛᴜᴋ ᴍᴇɴᴅɪᴛᴇᴋsɪ ʟɪɴᴋ ɢʀᴏᴜᴘ, ʙᴜᴋᴀɴ ᴀᴋᴜɴ ᴘʀɪʙᴀᴅɪ!!
• ᴋᴀʟᴀᴜ ᴇʀᴏʀ ʙᴏᴛɴʏᴀ ᴀɴᴅᴀ sɪʟᴀʜᴋᴀɴ ᴋᴇ ʟɪᴠᴇ ᴄʜᴀᴛ !!
• Jɪᴋᴀ ᴀndᴀ ᴘᴇʀɢᴀɴᴛɪᴀɴ ʟɪɴᴋ, ᴛɪᴅᴀᴋ ᴋᴏɴғɪʀᴍᴀsɪ ʟᴀɴɢsᴜɴɢ,
ᴅᴀɴ ʙᴏᴛ ᴍᴇʀᴇsᴘᴏɴ ᴅᴇɴɢᴀɴ ʟɪɴᴋ ᴀᴅᴀ ᴛɪᴅᴀᴋ ᴛᴇʀᴅᴀғᴛᴀʀ ɪᴛᴜ ʙᴜᴋᴀɴ ᴋᴇsᴀʟᴀʜ ᴋᴀᴍɪ!!
•Jɪᴋᴀ ᴀɴᴅᴀ ʙᴇʟᴜᴍ Jᴏɪɴ ɢʀᴏᴜᴘ ᴍᴀᴋᴀ ʙᴏᴛ ᴀᴋᴀɴ ᴍᴇɴʏᴜʀᴜʜ Jᴏɪɴ ɢʀᴏᴜᴘ ᴛᴇʀʟᴇʙɪʜ ᴅᴀʜᴜʟᴜ,
•Jɪᴋᴀ sᴜᴅᴀʜ Jᴏɪɴ ɢʀᴏᴜᴘɴʏᴀ, ʟᴀɴɢsᴜɴɢ ᴋɪʀɪᴍ ᴋᴀᴛᴀ ᴋᴀᴛᴀ ᴛᴀɢᴀʟʟɴʏᴀ sᴀJᴀ!!
━━━━━━━━━━━━━━━━━━━━━━━

💡 Gunakan bot dengan bijak!
"""

    keyboard = [
        [InlineKeyboardButton("🛍️ MY STORE", url="https://t.me/storegarf")]
    ]

    try:
        url = "https://i.ibb.co/rf5pNpck/file-00000000d14c71fa9909f192b1de2818.png"
        response = requests.get(url)
        image = BytesIO(response.content)

        update.message.reply_photo(
            photo=image,
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        print(f"[ERROR PHOTO]: {e}")
        update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ================= REGISTER =================

def register_menu(dp):
    dp.add_handler(CommandHandler("menu", menu_cmd))
