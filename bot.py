import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": user_message}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        bot_reply = res_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        bot_reply = "죄송합니다, 제미나이 API 처리 중 오류가 발생했습니다."

    await context.bot.send_message(chat_id=chat_id, text=bot_reply)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    app.run_polling()
