import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
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

user_links = {}

def main_buttons():
    keyboard = [
        [
            InlineKeyboardButton("💡 How to Use", callback_data="help"),
            InlineKeyboardButton("❤️ Support Us", callback_data="donate")
        ],
        [
            InlineKeyboardButton("🔗 Share with Friends", url=f"https://t.me/share/url?url=https://t.me/{BOT_USERNAME}&text=Download%20videos%20easily!")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def quality_buttons():
    keyboard = [
        [
            InlineKeyboardButton("🎬 Video", callback_data="dl_video"),
            InlineKeyboardButton("🎵 Audio", callback_data="dl_audio")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    text = (
        f"👋 <b>Hi {user_first_name}! Welcome to Video Downloader Bot!</b>\n\n"
        "<b>How to use:</b>\n"
        "1. Open any social network (YouTube, Facebook, Instagram, TikTok, etc.).\n"
        "2. Copy the video link.\n"
        "3. Send the link here to download!\n\n"
        "<blockquote>👇 <b>SEND ME ANY VIDEO LINK NOW!</b> 📥</blockquote>"
    )
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=main_buttons())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "💡 <b>How to use this bot:</b>\n\n"
        "• Copy any public video link from YouTube, Facebook, Instagram, TikTok, etc.\n"
        "• Paste and send it to this chat.\n"
        "• Choose Video or Audio format!\n"
        "• Wait a few seconds, and the file will be sent to you!"
    )
    await update.message.reply_text(help_text, parse_mode='HTML', reply_markup=main_buttons())

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
    await update.message.reply_text(donate_text, parse_mode='HTML', reply_markup=main_buttons())

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 <b>Bot Status:</b> Online & Working Fine!", parse_mode='HTML')

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("http"):
        return

    user_id = update.effective_user.id
    user_links[user_id] = url

    await update.message.reply_text(
        "⚙️ <b>Select Format to Download:</b>",
        parse_mode='HTML',
        reply_markup=quality_buttons()
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "help":
        await help_command(query, context)
        return
    elif query.data == "donate":
        await donate_command(query, context)
        return

    url = user_links.get(user_id)
    if not url:
        await query.edit_message_text("❌ Link expired. Please send the link again.")
        return

    if query.data in ["dl_video", "dl_audio"]:
        is_audio = query.data == "dl_audio"
        mode_str = "Audio" if is_audio else "Video"
        
        await query.edit_message_text(f"⏳ Downloading <b>{mode_str}</b>...", parse_mode='HTML')

        file_name = f"{query.message.message_id}.mp4" if not is_audio else f"{query.message.message_id}.m4a"

        # YouTube Bypass Options Integrated Here
        ydl_opts = {
            'outtmpl': file_name,
            'max_filesize': 50 * 1024 * 1024,
            'quiet': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            }
        }

        if is_audio:
            ydl_opts['format'] = 'bestaudio/best'
        else:
            ydl_opts['format'] = 'best[ext=mp4]/best'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            await query.edit_message_text("📤 Uploading file to Telegram...")
            caption_text = f"Downloaded via @{BOT_USERNAME}\n✨ Share with your friends!"

            with open(file_name, 'rb') as file:
                if is_audio:
                    await query.message.reply_audio(audio=file, caption=caption_text, reply_markup=main_buttons())
                else:
                    await query.message.reply_video(video=file, caption=caption_text, reply_markup=main_buttons())
            
            await query.delete_message()

        except Exception as e:
            await query.edit_message_text("❌ Download failed! Video might be over 50MB or blocked by platform.")

        finally:
            if os.path.exists(file_name):
                os.remove(file_name)
            user_links.pop(user_id, None)

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    print("Bot is running...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("legal", legal_command))
    app.add_handler(CommandHandler("donate", donate_command))
    app.add_handler(CommandHandler("status", status_command))
    
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    
    app.run_polling(drop_pending_updates=True)
