
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "YOUR_TELEGRAM_TOKEN"

# ===== DATABASE =====
def get_links(keyword=None):
    conn = sqlite3.connect("affiliate.db")
    c = conn.cursor()

    if keyword:
        c.execute("SELECT product, url FROM links WHERE product LIKE ?", (f"%{keyword}%",))
    else:
        c.execute("SELECT product, url FROM links")

    results = c.fetchall()
    conn.close()
    return results

def add_user(user_id):
    conn = sqlite3.connect("affiliate.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (platform, user_id) VALUES (?, ?)", ("telegram", str(user_id)))
    conn.commit()
    conn.close()

# ===== COMMANDS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    add_user(user_id)
    await update.message.reply_text("🔥 Welcome! Send /deals or type a product (e.g. laptop)")

async def deals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    links = get_links()
    if links:
        msg = "\n\n".join([f"🛒 {p}\n{u}" for p, u in links])
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("No deals available yet.")

async def keyword_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyword = update.message.text
    links = get_links(keyword)

    if links:
        msg = "\n\n".join([f"🛒 {p}\n{u}" for p, u in links])
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ No deals found for that.")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("deals", deals))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, keyword_search))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
