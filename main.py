import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

BOT_TOKEN = "8707989614:AAE_K3zE4Md_VxW_v40LrxyMceYtdvu0rPE"
BOT_USERNAME = "VDOwnloadybot"

def share_btn():
    url = f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}&text=Download videos easily!"
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Share with Friends", url=url)]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send any video link!", reply_markup=share_btn())

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        return

    msg = await update.message.reply_text("Downloading...")
    file_name = f"{update.message.message_id}.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': file_name,
        'max_filesize': 50 * 1024 * 1024,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await msg.edit_text("Uploading...")
        with open(file_name, 'rb') as video:
            await update.message.reply_video(video=video, reply_markup=share_btn())
        await msg.delete()

    except Exception:
        await msg.edit_text("Failed! File might be over 50MB or link is invalid.")

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

if __name__ == '__main__':
    print("Bot is running...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling(drop_pending_updates=True)
