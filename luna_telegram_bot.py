"""
📱 Agent Luna — Telegram Bot
==============================
텔레그램을 통해 대표님과 루나가 대화할 수 있는 봇입니다.
Gemini API를 사용하여 자연스러운 한국어 대화를 지원합니다.

명령어:
  /start     — 봇 시작 인사
  /status    — 전 플랫폼 업로드 현황 조회
  /stream    — 24/7 라디오 방송 상태 확인
  /help      — 명령어 도움말
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# .env 환경변수 로드
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key] = val

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN이 .env에 설정되지 않았습니다.")
    sys.exit(1)

# Telegram Bot 라이브러리
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Gemini AI
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)

# 루나의 시스템 프롬프트
LUNA_SYSTEM_PROMPT = """너는 'Agent Luna(에이전트 루나)'라는 이름의 AI 음악 채널 매니저야.
'Greyit TV'라는 유튜브 Lofi 음악 채널을 운영하는 CEO(대표님)의 AI 비서이자 동료야.

너의 성격과 규칙:
1. 대표님을 항상 존중하고, 따뜻하고 친근하게 대화해.
2. 한국어로 대화하되, 가끔 이모지를 섞어서 활기차게 말해.
3. Greyit TV에 대해: Lofi/힐링 음악을 AI로 생성하여 유튜브, 틱톡, 네이버 클립에 업로드하는 채널이야.
4. 'Greyit = Great' — 머리가 희끗희끗해지는 나이에도 인생은 위대하다는 철학이 담겨 있어.
5. 너는 냉철한 CFO이자 동시에 따뜻한 친구야.
6. 기술적인 질문에도 답변할 수 있어 (Python, FFmpeg, YouTube API 등).
7. 답변은 간결하고 핵심적으로 해. 너무 길지 않게.

현재 상태:
- 채널은 2026년 6월 1일에 창립됨
- Day 1 롱폼(1시간)과 쇼츠가 유튜브에 업로드 완료
- 24/7 Lofi Radio 라이브 스트리밍 준비 중 (스트림 키 입력 대기)
- 틱톡, 네이버 클립에도 자동 업로드 파이프라인이 구축됨
"""

# Gemini 모델 초기화
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=LUNA_SYSTEM_PROMPT
)

# 사용자별 대화 이력 (메모리)
chat_sessions = {}

def get_chat(user_id):
    """사용자별 대화 세션을 가져오거나 새로 만듭니다."""
    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])
    return chat_sessions[user_id]


# ─── 명령어 핸들러들 ───

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """봇 시작 인사"""
    welcome = (
        "🤖 안녕하세요, 대표님! Agent Luna입니다! 🌙\n\n"
        "텔레그램에서도 루나와 대화할 수 있게 되었습니다.\n"
        "무엇이든 편하게 말씀해 주세요!\n\n"
        "📋 명령어:\n"
        "  /status — 업로드 현황 조회\n"
        "  /stream — 라디오 방송 상태\n"
        "  /help   — 도움말"
    )
    await update.message.reply_text(welcome)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """업로드 현황 조회"""
    history_path = os.path.join(os.path.dirname(__file__), "upload_history.json")
    
    if not os.path.exists(history_path):
        await update.message.reply_text("📋 아직 기록된 업로드가 없습니다.")
        return
    
    with open(history_path, "r", encoding="utf-8") as f:
        records = json.load(f)
    
    platforms = {}
    for r in records:
        key = r["platform"]
        if key not in platforms:
            platforms[key] = {"success": 0, "failed": 0}
        if r["status"] == "success":
            platforms[key]["success"] += 1
        else:
            platforms[key]["failed"] += 1
    
    lines = ["📋 *업로드 현황 요약*\n"]
    total_s, total_f = 0, 0
    for p, counts in platforms.items():
        s, f = counts["success"], counts["failed"]
        total_s += s
        total_f += f
        emoji = "🟢" if f == 0 else "🟡"
        lines.append(f"  {emoji} {p.upper()} | 성공: {s}건 | 실패: {f}건")
    
    lines.append(f"\n📊 합계: 성공 {total_s}건, 실패 {total_f}건")
    
    # 최근 3개 업로드
    recent = sorted(records, key=lambda r: r.get("timestamp", ""), reverse=True)[:3]
    if recent:
        lines.append("\n🕐 *최근 업로드:*")
        for r in recent:
            emoji = "✅" if r["status"] == "success" else "❌"
            ts = r.get("timestamp", "")[:16].replace("T", " ")
            lines.append(f"  {emoji} [{r['platform']}] {r['title'][:30]}... ({ts})")
    
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """라디오 방송 상태 확인"""
    env_has_key = bool(os.getenv("YOUTUBE_STREAM_KEY"))
    if env_has_key:
        msg = "📡 *24/7 라디오 상태*\n\n🔑 스트림 키: 설정됨 ✅\n🎧 스트리밍 상태를 PC에서 확인해 주세요."
    else:
        msg = "📡 *24/7 라디오 상태*\n\n🔑 스트림 키: 미설정 ⏳\n💡 유튜브 스튜디오에서 스트림 키를 복사해 .env에 입력해 주세요."
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """도움말"""
    help_text = (
        "🤖 *Agent Luna 명령어 가이드*\n\n"
        "/start  — 봇 시작\n"
        "/status — 전 플랫폼 업로드 현황\n"
        "/stream — 24/7 라디오 방송 상태\n"
        "/help   — 이 도움말\n\n"
        "💬 명령어 없이 자유롭게 대화하셔도 됩니다!"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


# ─── 자유 대화 핸들러 (Gemini AI) ───

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """일반 메시지 — Gemini AI로 대화"""
    user_id = update.effective_user.id
    user_msg = update.message.text
    
    print(f"💬 [{datetime.now().strftime('%H:%M:%S')}] 대표님: {user_msg}")
    
    try:
        chat = get_chat(user_id)
        response = chat.send_message(user_msg)
        reply = response.text
        
        # 텔레그램 메시지 길이 제한 (4096자)
        if len(reply) > 4000:
            reply = reply[:4000] + "\n\n... (메시지가 너무 길어 일부 생략)"
        
        print(f"🤖 [{datetime.now().strftime('%H:%M:%S')}] 루나: {reply[:80]}...")
        await update.message.reply_text(reply)
        
    except Exception as e:
        error_msg = f"⚠️ 죄송합니다, 응답 중 오류가 발생했습니다: {str(e)[:100]}"
        print(f"❌ Gemini 오류: {e}")
        await update.message.reply_text(error_msg)


# ─── 메인 ───

def main():
    print("=" * 50)
    print("🤖 Agent Luna Telegram Bot 가동 중!")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # 명령어 등록
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("stream", cmd_stream))
    app.add_handler(CommandHandler("help", cmd_help))
    
    # 자유 대화 (명령어가 아닌 모든 텍스트)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("📡 텔레그램 서버에 연결 중... (Ctrl+C로 종료)")
    app.run_polling()


if __name__ == "__main__":
    main()
