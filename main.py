import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Render Free Plan Health Check Handler
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    server.serve_forever()

BOT_TOKEN = "8707989614:AAE_K3zE4Md_VxW_v40LrxyMceYtdvu0rPE"
BOT_USERNAME = "VDOwnloadybot"

def share_btn():
    url = f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}&text=Download videos easily!"
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Share with Friends", url=url)]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>How to use:</b>\n"
        "1. Open any social network (YouTube, Facebook, Instagram, TikTok, etc.).\n"
        "2. Copy the video link.\n"
        "3. Send the link here to download!\n\n"
        "Send me any video link now!"
    )
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=share_btn())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "💡 <b>How to use this bot:</b>\n\n"
        "• Copy any public video link from Facebook, Instagram, TikTok, YouTube Shorts, or Pinterest.\n"
        "• Paste and send it to this chat.\n"
        "• Wait a few seconds, and the video will be sent to you!"
    )
    await update.message.reply_text(help_text, parse_mode='HTML')

async def legal_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    legal_text = (
        "⚖️ <b>Legal Info:</b>\n\n"
        "This bot does not host or store any videos on its server. "
        "All media content is fetched directly from third-party social platforms for personal educational use only."
    )
    await update.message.reply_text(legal_text, parse_mode='HTML')

async def donate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    donate_text = (
        "❤️ <b>Support Video Downloader Bot</b>\n\n"
        "এই বটটি সবার জন্য সম্পূর্ণ ফ্রি! সার্ভার সচল রাখতে ও ফ্রি সেবা বজায় রাখতে আপনার ইচ্ছেমতো যেকোনো সহায়তার জন্য ধন্যবাদ:\n\n"
        "📱 <b>bKash (Personal):</b> <code>01794419546</code>\n"
        "🪙 <b>Binance Pay UID:</b> <code>927944043</code>\n\n"
        "আপনার সহযোগিতার জন্য অনেক অনেক ধন্যবাদ! 🙏"
    )
    await update.message.reply_text(donate_text, parse_mode='HTML', reply_markup=share_btn())

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
    # Start web server thread for Render
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    print("Bot is running...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("legal", legal_command))
    app.add_handler(CommandHandler("donate", donate_command))
    app.add_handler(CommandHandler("support", donate_command))
    
    # Message Handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    app.run_polling(drop_pending_updates=True)
