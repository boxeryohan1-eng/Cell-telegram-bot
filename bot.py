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

# ⚠️ 여기에 본인의 텔레그램 봇 아이디를 입력하세요 (예: "@MyAwesome_bot")
BOT_USERNAME = "@my_cell_pd_bot" 

# 제미나이 공식 라이브러리 설정 (gemini-3-flash-preview 적용)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3-flash-preview")

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

    # 1. 봇 멘션(@봇아이디)이 포함되어 있는지 확인
    if BOT_USERNAME in user_message:
        # 멘션 문자열 제거 후 순수 질문 내용만 추출
        cleaned_message = user_message.replace(BOT_USERNAME, "").strip()
        
        # 태그만 올리고 질문이 없을 경우 처리
        if not cleaned_message:
            await context.bot.send_message(chat_id=chat_id, text="네! 무엇을 도와드릴까요?")
            return

        try:
            response = model.generate_content(cleaned_message)
            bot_reply = response.text
        except Exception as e:
            bot_reply = f"제미나이 API 오류 발생: {str(e)}"

        await context.bot.send_message(chat_id=chat_id, text=bot_reply)
    else:
        # 태그가 없으면 아무 작업도 하지 않고 무시
        pass

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
