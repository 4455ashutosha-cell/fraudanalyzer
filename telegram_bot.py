
"""
WebGuard AI - Telegram Bot
India's Real Problem: Telegram pe fake jobs / betting / adult scams
Run: pip install python-telegram-bot fastapi requests
Env: BOT_TOKEN from @BotFather
"""
import os, requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")  # FastAPI 8-engine

REAL_SCAM_EXAMPLES = {
    "job": "Telegram pe 90% fake jobs: 'Work from home 50k, Telegram pe contact karo, Registration fee 499 Paytm karo' - Ye sab WebGuard pakad leta hai.",
    "betting": "Aviator game / 1xBet predictor - 'Double money in 2 min' - Students lakhs gawa dete hain. Bot instantly RED batayega.",
    "adult": "Adult link forward hote hain groups me - Bot blur nahi but warning dega ki ye adult category hai."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ *WebGuard AI - Telegram Scam Shield*\n\n"
        "India me Telegram pe sabse zyada scam hota hai - Fake Jobs + Betting + Phishing\n\n"
        "Bas koi bhi suspicious link bhejo, main 8 engines se check karke bataunga:\n"
        "• Score /100\n• RED/YELLOW/GREEN\n• Kyu risky hai (Hindi me)\n\n"
        "Try karo: `google-careers-apply.com` ya `1xbet-aviator-win.com`\n\n"
        "_Privacy: Tumhara IP trace nahi hota. Link sirf analysis ke liye use hota hai, log nahi hota._",
        parse_mode="Markdown"
    )

async def scan_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    # extract url
    import re
    urls = re.findall(r'https?://\S+|\S+\.\S+', text)
    if not urls:
        await update.message.reply_text("Link bhejo bhai, jaise: https://google-login-verify.com")
        return
    url = urls[0]
    if not url.startswith("http"):
        url = "https://" + url

    try:
        # Call FastAPI backend (no IP logging)
        resp = requests.get(f"{BACKEND_URL}/scan", params={"url": url}, timeout=10)
        data = resp.json()
        color_emoji = "🔴" if data["verdict"]=="RED" else "🟡" if data["verdict"]=="YELLOW" else "🟢"
        reasons = "\n".join([f"• {r}" for r in data["reasons"][:5]])
        
        reply = (
            f"{color_emoji} *{data['verdict']} - {data['trust']}/100*\n"
            f"URL: `{url}`\n\n"
            f"*Kyu risky hai?*\n{reasons}\n\n"
            f"Flags: {'🔞 Adult' if data['flags']['adult'] else ''} {'🎰 Betting' if data['flags']['betting'] else ''}\n\n"
            f"_IP Privacy: Tumhara IP trace nahi hua. Ye analysis 100% anonymous hai._\n\n"
            f"Full protection ke liye Extension download karo: webguard-ai.vercel.app"
        )
        # Add real story if betting/job
        if data["flags"]["betting"]:
            reply += f"\n\n⚠️ *Real India Story:* {REAL_SCAM_EXAMPLES['betting']}"
        if data["engines"]["jobFraud"]["score"]>0 or data["engines"]["ai_fake"]["score"]>0:
            reply += f"\n\n⚠️ *Real India Story:* {REAL_SCAM_EXAMPLES['job']}"

        await update.message.reply_text(reply, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}\nBackend URL check karo: {BACKEND_URL}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, scan_link))
    print("Telegram Bot Running... Real scam protection for India")
    app.run_polling()
