"""Link command handler."""
from telegram import Update
from telegram.ext import ContextTypes

from app.db.session import async_session_maker
from app.services.user_service import UserService


async def link_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Link Telegram account to Web Dashboard account."""
    if not update.effective_user or not update.message:
        return

    # Check for arguments
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "⚠️ Please provide the link code from the dashboard.\n"
            "Usage: /link 123456"
        )
        return

    code = context.args[0]
    telegram_id = update.effective_user.id

    async with async_session_maker() as db:
        user_service = UserService(db)
        success = await user_service.link_telegram_account(code, telegram_id)

    if success:
        await update.message.reply_text(
            "✅ Accounts linked successfully!\n"
            "Your transactions will now appear in your Web Dashboard."
        )
    else:
        await update.message.reply_text(
            "❌ Invalid or expired code.\n"
            "Please generate a new code from your dashboard settings."
        )
