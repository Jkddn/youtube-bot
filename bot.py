import os, asyncio, yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DOWNLOAD_DIR = "/tmp/downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 YouTube link bhejo!")

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("❌ YouTube link bhejo!")
        return
    msg = await update.message.reply_text("⏳ Download ho raha hai...")
    try:
        ydl_opts = {
            "format": "best[filesize<50M]/best",
            "outtmpl": os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s"),
            "quiet": True,
            "extractor_args": {"youtube": {"player_client": ["android"]}},
        }
        loop = asyncio.get_event_loop()
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info), info.get("title","Video")
        filename, title = await loop.run_in_executor(None, download)
        await msg.edit_text("📤 Upload ho raha hai...")
        with open(filename, "rb") as f:
            await update.message.reply_video(video=f, caption=f"✅ {title}")
        await msg.delete()
        os.remove(filename)
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)[:300]}")

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    print("✅ Bot chalu ho gaya!")
    app.run_polling(drop_pending_updates=True)
