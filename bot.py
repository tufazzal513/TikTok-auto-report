import asyncio
import re
import time
import random
import threading
from typing import Dict, List
import requests
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from fake_useragent import UserAgent

# ============= SYSTEM_CONFIG =============
BOT_TOKEN = "7992726429:AAHMIvwT-oCyqXmdc1X6g2g6VCmJHQfcB7k"
DEVELOPER_USERNAME = "Aegriss"
CHANNEL_LINK = "https://t.me/+xScEFigNbXMzNGM0"

SESSION_POOL = [
    "a0f49aaf1ecd041dc6469aa9de3e8a8b", "35af0ab71fa286b4d32fa794eab67766",
    "f00e754b271ebcbeb1ec81d1b8b74c94", "774cb9362213b37b4bd51528d3e30295",
    "2b37fd4151b4eaf7196f5f5e7e659f64", "e75ed27910bc3b0d134faa20f7d6be86",
]

bot = AsyncTeleBot(BOT_TOKEN)
user_data: Dict[int, Dict] = {}
active_jobs: Dict[int, threading.Thread] = {}

# ============= CORE_FUNCTIONS =============
def extract_tiktok_id(username_or_url: str) -> str:
    pattern = r'(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@([a-zA-Z0-9_.]+)'
    match = re.search(pattern, username_or_url)
    if match:
        return match.group(1)
    if username_or_url.startswith('@'):
        return username_or_url[1:]
    return username_or_url

def get_user_id(username: str) -> str:
    headers = {
        'User-Agent': UserAgent().random,
        'Accept': 'text/html,application/xhtml+xml'
    }
    try:
        resp = requests.get(f'https://www.tiktok.com/@{username}', headers=headers, timeout=10)
        match = re.search(r'"user":{"id":"(\d+)"', resp.text)
        return match.group(1) if match else None
    except:
        return None

def send_report(session_id: str, target_id: str) -> bool:
    url = "https://api16-normal-c-alisg.tiktokv.com/aweme/v2/aweme/feedback/"
    params = {
        'report_type': 'user',
        'object_id': target_id,
        'owner_id': target_id,
        'reason': '9004',
        'lang': 'en',
        '_rticket': str(int(time.time() * 1000)),
        'aid': '1340',
        'ts': str(int(time.time()))
    }
    headers = {
        'User-Agent': 'com.zhiliaoapp.musically.go/430103 (Linux; Android 15)',
        'Cookie': f'sessionid={session_id}; sid_tt={session_id}'
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        return 'status_code":0' in resp.text
    except:
        return False

# ============= MAIN_MESSAGE_TEMPLATE =============
def get_main_message() -> str:
    return """
─── ❮ 𝗧𝗶𝗸𝗧𝗼𝗸 𝗥𝗲𝗽𝗼𝗿𝘁 𝗘𝗻𝗴𝗶𝗻𝗲 ❯ ───

🛡️ Smart Automated Reporting System
🚀 Your primary tool to disable TikTok accounts with one click.

🔍 Status: Online and Ready..
──────────────────
« Awaiting Target Definition »
"""

# ============= INTERFACE RENDERERS =============
def render_dashboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🎯 Set Target", callback_data="set_target", style="primary"),
        InlineKeyboardButton("🔑 Add Sessions", callback_data="add_sessions", style="success")
    )
    keyboard.add(
        InlineKeyboardButton("⚡ Attack Speed", callback_data="intensity", style="primary"),
        InlineKeyboardButton("💥 Launch Attack", callback_data="launch", style="danger")
    )
    keyboard.add(
        InlineKeyboardButton("📊 Statistics", callback_data="stats", style="primary"),
        InlineKeyboardButton("🛑 Stop Attack", callback_data="stop", style="danger")
    )
    keyboard.add(
        InlineKeyboardButton("👨‍💻 Developer", url=f"https://t.me/{DEVELOPER_USERNAME}", style="primary"),
        InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK, style="success")
    )
    return keyboard

def render_intensity_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("⚡ Extreme (2s)", callback_data="int_2", style="danger"),
        InlineKeyboardButton("🚀 Fast (5s)", callback_data="int_5", style="danger")
    )
    keyboard.add(
        InlineKeyboardButton("🐢 Medium (10s)", callback_data="int_10", style="primary"),
        InlineKeyboardButton("⚠️ Slow (15s)", callback_data="int_15", style="primary")
    )
    keyboard.add(
        InlineKeyboardButton("🔙 Back", callback_data="back", style="primary")
    )
    return keyboard

def format_progress_bar(current: int, total: int, width: int = 20) -> str:
    filled = int(width * current / total)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {current}/{total} Success"

# ============= REPORT_ENGINE =============
async def execute_report_batch(user_id: int, target_username: str, sessions: List[str], intensity: int, message_id: int, chat_id: int):
    target_id = get_user_id(target_username)
    if not target_id:
        await bot.edit_message_text("❌ Target not found or account protected", chat_id, message_id)
        return
    
    total = len(sessions)
    success = 0
    
    for i, session in enumerate(sessions):
        if user_id in active_jobs and not active_jobs[user_id].is_alive():
            await bot.edit_message_text("🛑 Attack stopped", chat_id, message_id)
            return
        
        if send_report(session, target_id):
            success += 1
        
        progress = format_progress_bar(success, total)
        await bot.edit_message_text(
            f"🔄 Sending reports...\n{progress}\n\n✅ Success: {success}\n❌ Failed: {i+1-success}\n📊 Rate: {(success/(i+1))*100:.1f}%",
            chat_id, message_id
        )
        await asyncio.sleep(random.uniform(1, 2))
        
        if (i + 1) % 10 == 0 and i + 1 < total:
            await asyncio.sleep(intensity)
    
    await bot.edit_message_text(
        f"✅ Attack Completed\n━━━━━━━━━━━━━━\n🎯 Target: @{target_username}\n✅ Success: {success}\n❌ Failed: {total-success}\n📊 Rate: {(success/total)*100:.1f}%",
        chat_id, message_id
    )
    if user_id in active_jobs:
        del active_jobs[user_id]

# ============= HANDLERS =============
@bot.message_handler(commands=['start'])
async def start_command(message):
    user_data[message.from_user.id] = {
        'target': None, 
        'intensity': 10, 
        'sessions': SESSION_POOL.copy()
    }
    await bot.send_message(
        message.chat.id,
        get_main_message(),
        reply_markup=render_dashboard()
    )

@bot.callback_query_handler(func=lambda call: True)
async def handle_callbacks(call: CallbackQuery):
    user_id = call.from_user.id
    data = call.data
    
    if data == "add_sessions":
        await bot.edit_message_text(
            "🔐 Add New Sessions\n━━━━━━━━━━\nEnter the quantity first\nExample: 10\nThen send sessions, one per line",
            call.message.chat.id, call.message.message_id
        )
        user_data[user_id]['waiting_for_session_count'] = True
    
    elif data == "set_target":
        await bot.edit_message_text(
            "🎯 Set Target\n━━━━━━━━━━\nSend TikTok link or username\nExample: @username",
            call.message.chat.id, call.message.message_id
        )
        user_data[user_id]['waiting_for_target'] = True
    
    elif data == "intensity":
        await bot.edit_message_text(
            "⚡ Select attack speed", 
            call.message.chat.id, 
            call.message.message_id, 
            reply_markup=render_intensity_keyboard()
        )
    
    elif data.startswith("int_"):
        intensity = int(data.split('_')[1])
        if user_id in user_data:
            user_data[user_id]['intensity'] = intensity
        await bot.answer_callback_query(call.id, f"Speed set to {intensity} seconds")
        msg_text = get_main_message() + f"\n\n✅ Speed: {intensity} seconds"
        await bot.edit_message_text(msg_text, call.message.chat.id, call.message.message_id, reply_markup=render_dashboard())
    
    elif data == "launch":
        if user_id in active_jobs:
            await bot.answer_callback_query(call.id, "⚠️ An attack is already running")
            return
        target = user_data.get(user_id, {}).get('target')
        if not target:
            await bot.answer_callback_query(call.id, "❌ No target set")
            return
        
        sessions = user_data[user_id].get('sessions', SESSION_POOL)
        intensity = user_data[user_id].get('intensity', 10)
        
        msg = await bot.edit_message_text("🚀 Preparing attack...", call.message.chat.id, call.message.message_id)
        
        def run_async():
            asyncio.run(execute_report_batch(user_id, target, sessions, intensity, msg.message_id, call.message.chat.id))
        
        thread = threading.Thread(target=run_async)
        active_jobs[user_id] = thread
        thread.start()
    
    elif data == "stats":
        stats = user_data.get(user_id, {})
        sessions_count = len(stats.get('sessions', []))
        status = "🔥 Active" if user_id in active_jobs else "✅ Idle"
        stats_text = get_main_message() + f"""

📊 Statistics
━━━━━━━━━━━━
🎯 Target: {stats.get('target', 'None')}
⚡ Speed: {stats.get('intensity', 10)}s
🔑 Sessions: {sessions_count}
📌 Status: {status}"""
        await bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, reply_markup=render_dashboard())
    
    elif data == "stop":
        if user_id in active_jobs:
            del active_jobs[user_id]
            msg_text = get_main_message() + "\n\n🛑 Attack stopped successfully"
            await bot.edit_message_text(msg_text, call.message.chat.id, call.message.message_id, reply_markup=render_dashboard())
    
    elif data == "back":
        await bot.edit_message_text(get_main_message(), call.message.chat.id, call.message.message_id, reply_markup=render_dashboard())

# ============= MESSAGE HANDLERS =============
@bot.message_handler(func=lambda message: True)
async def handle_messages(message):
    user_id = message.from_user.id
    if user_id not in user_data: return
    
    if user_data[user_id].get('waiting_for_session_count'):
        try:
            count = int(message.text.strip())
            user_data[user_id].update({'expected_session_count': count, 'waiting_for_session_count': False, 'waiting_for_sessions': True})
            await bot.send_message(message.chat.id, f"✅ Enter {count} sessions (32 alphanumeric chars per line)")
        except:
            await bot.send_message(message.chat.id, "❌ Invalid number")
    
    elif user_data[user_id].get('waiting_for_sessions'):
        sessions = re.findall(r'[a-f0-9]{32}', message.text)
        user_data[user_id]['sessions'].extend(sessions)
        await bot.send_message(message.chat.id, f"✅ Added {len(sessions)} sessions.", reply_markup=render_dashboard())
        user_data[user_id]['waiting_for_sessions'] = False
        
    elif user_data[user_id].get('waiting_for_target'):
        username = extract_tiktok_id(message.text)
        user_data[user_id].update({'target': username, 'waiting_for_target': False})
        await bot.send_message(message.chat.id, f"✅ Target set: @{username}", reply_markup=render_dashboard())

if __name__ == '__main__':
    asyncio.run(bot.polling(non_stop=True))
