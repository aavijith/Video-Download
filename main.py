import os
import time
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

user_data_store = {}

def background_cleanup_task():
    while True:
        try:
            for file in os.listdir('.'):
                if file.endswith(('.mp4', '.m4a', '.webm', '.mp3')) and not file.startswith('main'):
                    file_path = os.path.join('.', file)
                    if time.time() - os.path.getmtime(file_path) > 600:
                        os.remove(file_path)
        except Exception as e:
            print(f"Cleanup Error: {e}")
        time.sleep(600)

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
            InlineKeyboardButton("🎬 HD Video (Best)", callback_data="dl_hd"),
            InlineKeyboardButton("🎬 SD Video (Fast)", callback_data="dl_sd")
        ],
        [
            InlineKeyboardButton("🎵 Audio (MP3/M4A)", callback_data="dl_audio")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    text = (
        f"👋 <b>Hi {user_first_name}! Welcome to Video Downloader Bot!</b>\n\n"
        "<b>How to use:</b>\n"
        "1. Open YouTube, Facebook, Instagram, TikTok, Twitter, Pinterest, etc.\n"
        "2. Copy the video link.\n"
        "3. Send the link here to download!\n\n"
        "<blockquote>👇 <b>SEND ME ANY SUPPORTED LINK NOW!</b> 📥</blockquote>"
    )
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=main_buttons())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "💡 <b>How to use this bot:</b>\n\n"
        "• Copy any public video link from YouTube, Facebook, Instagram, TikTok, Twitter/X, Pinterest, etc.\n"
        "• Paste and send it to this chat.\n"
        "• Preview details and choose preferred quality!\n\n"
        "✨ <i>All video links under 50MB are fully supported!</i>"
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
    processing_msg = await update.message.reply_text("🔍 <b>Fetching video details...</b>", parse_mode='HTML')
    
    ydl_info_opts = {'quiet': True, 'skip_download': True}
    video_title = "Downloaded Video"
    thumbnail_url = None

    try:
        with yt_dlp.YoutubeDL(ydl_info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_title = info.get('title', 'Downloaded Video')
            thumbnail_url = info.get('thumbnail', None)
    except Exception as e:
        print(f"Info Fetch Error: {e}")

    user_data_store[user_id] = {"url": url, "title": video_title}

    preview_text = (
        f"<b>📺 Video Preview:</b>\n"
        f"<code>{video_title}</code>\n\n"
        "⚙️ <b>Select your preferred quality/format below:</b>"
    )

    try:
        await processing_msg.delete()
    except:
        pass

    if thumbnail_url:
        await update.message.reply_photo(
            photo=thumbnail_url,
            caption=preview_text,
            parse_mode='HTML',
            reply_markup=quality_buttons()
        )
    else:
        await update.message.reply_text(
            text=preview_text,
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

    user_info = user_data_store.get(user_id)
    if not user_info:
        await query.edit_message_text("❌ Session expired. Please send the link again.")
        return

    url = user_info["url"]
    
    if query.data in ["dl_hd", "dl_sd", "dl_audio"]:
        if query.data == "dl_hd":
            mode_str = "HD Video"
            ydl_format = 'best[height<=720][filesize<50M]/best[height<=480]/worst'
            is_audio = False
        elif query.data == "dl_sd":
            mode_str = "SD Video"
            ydl_format = 'worst[ext=mp4]/worst'
            is_audio = False
        else:
            mode_str = "Audio"
            ydl_format = 'bestaudio/best'
            is_audio = True

        if query.message.photo:
            await query.edit_message_caption(caption=f"⏳ <b>Downloading {mode_str}... Please wait.</b>", parse_mode='HTML')
        else:
            await query.edit_message_text(f"⏳ <b>Downloading {mode_str}... Please wait.</b>", parse_mode='HTML')

        file_name = f"{query.message.message_id}.mp4" if not is_audio else f"{query.message.message_id}.m4a"
        
        ydl_opts = {
            'outtmpl': file_name,
            'quiet': True,
            'nocheckcertificate': True,
            'geo_bypass': True,
            'format': ydl_format
        }

        download_success = False
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
                if os.path.getsize(file_name) <= 52428800:
                    download_success = True
                else:
                    print("File exceeds 50MB limit after download.")
        except Exception as e:
            print(f"Download Error: {e}")

        if download_success:
            if query.message.photo:
                await query.edit_message_caption(caption="📤 <b>Uploading file to Telegram...</b>", parse_mode='HTML')
            else:
                await query.edit_message_text("📤 <b>Uploading file to Telegram...</b>", parse_mode='HTML')
                
            caption_text = f"<b>{user_info['title']}</b>\n\nDownloaded via @{BOT_USERNAME}\n✨ Share with your friends!"

            try:
                with open(file_name, 'rb') as file:
                    if is_audio:
                        await query.message.reply_audio(audio=file, caption=caption_text, parse_mode='HTML', reply_markup=main_buttons())
                    else:
                        await query.message.reply_video(video=file, caption=caption_text, parse_mode='HTML', reply_markup=main_buttons())
                await query.delete_message()
            except Exception as upload_err:
                await query.edit_message_text(f"❌ Upload failed: File might be larger than 50MB.")
        else:
            await query.edit_message_text("❌ Download failed! Video size is larger than 50MB or blocked by platform.")

        if os.path.exists(file_name):
            os.remove(file_name)
        user_data_store.pop(user_id, None)

if __name__ == '__main__':
    threading.Thread(target=background_cleanup_task, daemon=True).start()
    threading.Thread(target=run_dummy_server, daemon=True).start()
    
    print("Bot is fully adjusted and running...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("legal", legal_command))
    app.add_handler(CommandHandler("donate", donate_command))
    app.add_handler(CommandHandler("status", status_command))
    
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    
    app.run_polling(drop_pending_updates=True)
