import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# 로그 설정
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = os.getenv("TELEGRAM")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

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

    # 최신 모델명 적용 (gemini-2.5-flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": user_message}]}]}

    try:
        response = requests.post(url, headers=headers, json=data)
        res_json = response.json()
        
        if 'candidates' in res_json:
            bot_reply = res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            error_msg = res_json.get('error', {}).get('message', '알 수 없는 오류')
            bot_reply = f"제미나이 API 오류: {error_msg}"
    except Exception as e:
        bot_reply = f"오류가 발생했습니다: {str(e)}"

    await context.bot.send_message(chat_id=chat_id, text=bot_reply)

if __name__ == '__main__':
    # 백그라운드 웹서버 실행
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler(["start", "help"], handle_message))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    app.run_polling()
