from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler

# ================= HELP FITUR =================

def fitur_cmd(update, context):

    text = """
╭━━━━━━━━━━━━━━━━━━━━━━━╮
⚡ 𝗙𝗜𝗧𝗨𝗥 & 𝗣𝗘𝗡𝗝𝗘𝗟𝗔𝗦𝗔𝗡 𝗕𝗢𝗧 ⚡
╰━━━━━━━━━━━━━━━━━━━━━━━╯

🤖 BOT SYSTEM INFORMATION

Bot ini memiliki berbagai fitur otomatis untuk mempermudah pengelolaan group & partner system.

━━━━━━━━━━━━━━━━━━━━━━━

👤 USER FEATURES

⏰ /absen
➜ Sistem absensi otomatis 24 jam
➜ Digunakan untuk kehadiran member

📊 /rekab [nama]
➜ Rekap data TMO / jobdast partner
➜ Contoh: /rekab HYPERION

📄 /jobdesk
➜ Menampilkan pilihan jobdesk TMO
➜ Admin dapat mengatur isi jobdesk

🏷️ /tagall
➜ Menandai semua member di group

━━━━━━━━━━━━━━━━━━━━━━━

👑 OWNER FEATURES

📢 /bc
➜ Broadcast pesan ke semua user & group

👤 /addpj & /delpj
➜ Mengatur PJ (Penanggung Jawab bot)

🖼️ /addpict & /delpict
➜ Mengatur foto tampilan start bot

🤝 /addpartner & /delpartner
➜ Mengelola daftar partner bot

📋 /listpartner
➜ Melihat semua partner yang terdaftar

🔘 /addbuttontag
➜ Menambahkan tombol custom untuk tagall

📜 /addrules & /delrules
➜ Mengatur rules bot yang tampil di menu

💬 /addlivechat
➜ Mengaktifkan live chat admin dengan user

🌐 support sistem forcesub
➜ wajib join group sebelum menggunakan botnya

━━━━━━━━━━━━━━━━━━━━━━━

⚙️ SISTEM BOT

• Auto system support group
• Support partner management
• Support custom menu & button
• Support auto tagging system
• Support admin control panel
━━━━━━━━━━━━━━━━━━━━━━━

💡 Gunakan bot dengan bijak & sesuai aturan group!
"""

    keyboard = [
        [InlineKeyboardButton("🛍️ MY STORE", url="https://t.me/storegarf")]
    ]

    update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= REGISTER =================

def register_fitur(dp):
    dp.add_handler(CommandHandler("fitur", fitur_cmd))
