from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler

# ================= MENU COMMAND =================

def menu_cmd(update, context):
    text = """
╭━━━━━━━━━━━━━━━━━━━━━━━╮
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
• Jɪᴋᴀ ᴀᴅᴀ ᴘᴇʀɢᴀɴᴛɪᴀɴ ʟɪɴᴋ, ᴛɪᴅᴀᴋ ᴋᴏɴғɪʀᴍᴀsɪ ʟᴀɴɢsᴜɴɢ, 
  ᴅᴀɴ ʙᴏᴛ ᴍᴇʀᴇsᴘᴏɴ ᴅᴇɴɢᴀɴ ʟɪɴᴋ ᴀᴅᴀ ᴛɪᴅᴀᴋ ᴛᴇʀᴅᴀғᴛᴀʀ ɪᴛᴜ ʙᴜᴋᴀɴ ᴋᴇsᴀʟᴀʜ ᴋᴀᴍɪ!!

━━━━━━━━━━━━━━━━━━━━━━━

💡 Gunakan bot dengan bijak!
"""

    keyboard = [
        [InlineKeyboardButton("🛍️ MY STORE", url="https://t.me/storegarf")]
    ]

    update.message.reply_photo(
        photo="https://i.ibb.co/rf5pNpck/file-00000000d14c71fa9909f192b1de2818.png",
        caption=text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= REGISTER =================

def register_menu(dp):
    dp.add_handler(CommandHandler("menu", menu_cmd))
