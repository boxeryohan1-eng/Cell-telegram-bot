import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# 로그 설정
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 제미나이 공식 라이브러리 설정 (gemini-3-flash 모델 적용)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3-flash")

# Render 포트 바인딩 에러 방지용 가짜 웹서버
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    try:
        response = model.generate_content(user_message)
        bot_reply = response.text
    except Exception as e:
        bot_reply = f"제미나이 API 오류 발생: {str(e)}"

    await context.bot.send_message(chat_id=chat_id, text=bot_reply)

if __name__ == '__main__':
    # 백그라운드 웹서버 실행 (Render 대응)
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler(["start", "help"], handle_message))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    app.run_polling()
