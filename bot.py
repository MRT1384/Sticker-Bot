import asyncio
import os
from telegram import Update, Bot, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

emojis = ["🎲", "🎯", "🎳"]

enabled_chats = set()
emoji_index = 0

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    user = update.effective_user

    # اگر چت پرایوت است، هیچ محدودیتی نباشد (یا می‌توان False بدهیم)
    if chat.type == "private":
        return True  # یا True اگر می‌خوای owner بتونه از بات در پرایوت هم استفاده کنه

    # فقط برای گروه‌ها و سوپرگروه‌ها
    member = await context.bot.get_chat_member(chat.id, user.id)
    return member.status in (ChatMember.ADMINISTRATOR, ChatMember.OWNER)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ فقط ادمین‌ها می‌تونن ربات رو فعال کنن.")
        return
    enabled_chats.add(update.effective_chat.id)
    await update.message.reply_text("✅ ربات فعال شد.")

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("❌ فقط ادمین‌ها می‌تونن ربات رو متوقف کنن.")
        return
    enabled_chats.discard(update.effective_chat.id)
    await update.message.reply_text("⛔️ ربات متوقف شد.")

async def emoji_loop(bot: Bot):
    global emoji_index
    try:
        while True:
            for chat_id in list(enabled_chats):
                try:
                    await bot.send_dice(chat_id=chat_id, emoji=emojis[emoji_index])
                except Exception as e:
                    print(f"خطا در {chat_id}: {e}")
                    enabled_chats.discard(chat_id)
            emoji_index = (emoji_index + 1) % len(emojis)
            await asyncio.sleep(5)
    except asyncio.CancelledError:
        print("🛑 emoji_loop cancelled cleanly")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))

    # اجرای emoji_loop همزمان با run_polling
    async def start_emoji_loop(app: Application):
        asyncio.create_task(emoji_loop(app.bot))

    app.post_init = start_emoji_loop
    app.run_polling()

if __name__ == "__main__":
    main()