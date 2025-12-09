"""Telegram bot application with backend integration."""

import logging
from decimal import Decimal
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.bot.parsers import ExpenseParser
from app.bot.services import BotService
from app.config import get_settings
from app.db.session import async_session_maker
from app.models.transaction import TransactionType

settings = get_settings()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Initialize parser
expense_parser = ExpenseParser()


async def get_bot_service() -> BotService:
    """Get bot service with database session."""
    session = async_session_maker()
    return BotService(session)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    
    # Register/get user
    async with async_session_maker() as session:
        bot_service = BotService(session)
        db_user = await bot_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )
    
    welcome_message = (
        f"👋 Welcome to *Centavo*, {user.mention_markdown_v2()}\\!\n\n"
        "I'm your personal expense tracker\\. I can help you:\n"
        "• 💰 Track expenses and income\n"
        "• 📊 View spending reports\n"
        "• 📁 Organize by categories\n\n"
        "Just send me a message like:\n"
        "`50 lunch` or `\\+1000 salary`\n\n"
        "Use /help to see all commands\\."
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode="MarkdownV2",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = (
        "*Available Commands:*\n\n"
        "/start \\- Welcome message\n"
        "/help \\- Show this help\n"
        "/report \\- View your expense summary\n"
        "/categories \\- List all categories\n"
        "/settings \\- Your preferences\n\n"
        "*Quick Tips:*\n"
        "• Send `50 lunch` to log \\$50 expense\n"
        "• Use `\\+100 salary` for income\n"
        "• Currency: MXN\n"
    )
    
    await update.message.reply_text(
        help_text,
        parse_mode="MarkdownV2",
    )


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /report command."""
    user = update.effective_user
    
    async with async_session_maker() as session:
        bot_service = BotService(session)
        db_user = await bot_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )
        
        summary = await bot_service.get_month_summary(db_user.id)
    
    # Helper function to escape for MarkdownV2
    def escape_md(text: str) -> str:
        """Escape special characters for MarkdownV2."""
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        return text
    
    # Format amounts safely
    expenses = f"${summary['total_expenses']:.2f}".replace('.', '\\.')
    income = f"${summary['total_income']:.2f}".replace('.', '\\.')
    balance = f"${summary['balance']:.2f}".replace('.', '\\.')
    
    # Build report message
    report_lines = [
        f"*📊 {escape_md(summary['period'])} Report*\n",
        f"💸 *Expenses:* {expenses}",
        f"💰 *Income:* {income}",
        f"📈 *Balance:* {balance}",
        f"📝 *Transactions:* {summary['transaction_count']}\n",
    ]
    
    if summary['top_categories']:
        report_lines.append("*Top Categories:*")
        for cat_name, amount in summary['top_categories']:
            safe_name = escape_md(cat_name)
            safe_amount = f"${amount:.2f}".replace('.', '\\.')
            report_lines.append(f"  • {safe_name}: {safe_amount}")
    
    report_text = "\n".join(report_lines)
    
    await update.message.reply_text(
        report_text,
        parse_mode="MarkdownV2",
    )


async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /categories command."""
    user = update.effective_user
    
    async with async_session_maker() as session:
        bot_service = BotService(session)
        db_user = await bot_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )
        
        categories = await bot_service.get_categories(db_user.id)
    
    # Group by type
    expense_cats = [c for c in categories if c.type == TransactionType.EXPENSE]
    income_cats = [c for c in categories if c.type == TransactionType.INCOME]
    
    # Build message
    lines = ["*📁 Available Categories*\n"]
    
    if expense_cats:
        lines.append("*Expenses:*")
        for cat in expense_cats[:10]:  # Limit to 10
            safe_name = cat.name.replace('-', '\\-').replace('.', '\\.')
            lines.append(f"{cat.icon} {safe_name}")
        lines.append("")
    
    if income_cats:
        lines.append("*Income:*")
        for cat in income_cats[:10]:
            safe_name = cat.name.replace('-', '\\-').replace('.', '\\.')
            lines.append(f"{cat.icon} {safe_name}")
    
    categories_text = "\n".join(lines)
    
    await update.message.reply_text(
        categories_text,
        parse_mode="MarkdownV2",
    )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /settings command."""
    user = update.effective_user
    
    async with async_session_maker() as session:
        bot_service = BotService(session)
        db_user = await bot_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )
    
    settings_text = (
        f"*⚙️ Your Settings*\n\n"
        f"Telegram ID: `{user.id}`\n"
        f"Name: {user.mention_markdown_v2()}\n"
        f"Display Name: {db_user.display_name}\n"
        f"Currency: {db_user.default_currency}\n"
    )
    
    await update.message.reply_text(
        settings_text,
        parse_mode="MarkdownV2",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages (expense/income logging)."""
    user = update.effective_user
    text = update.message.text
    
    # Parse message
    parsed = expense_parser.parse(text)
    
    if not parsed:
        response = (
            "❌ I couldn't understand that\\.\n\n"
            "Try: `50 lunch` or `\\+1000 salary`\n"
            "Use /help for more examples\\."
        )
        await update.message.reply_text(response, parse_mode="MarkdownV2")
        return
    
    # Get/create user
    async with async_session_maker() as session:
        bot_service = BotService(session)
        db_user = await bot_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )
        
        # Try to find category if hint exists
        category_id = None
        matched_category = None
        
        if parsed.category_hint:
            matched_category = await bot_service.find_category_by_keyword(
                user_id=db_user.id,
                keyword=parsed.category_hint,
                transaction_type=parsed.type,
            )
            if matched_category:
                category_id = matched_category.id
        
        # Show category picker if no match
        if not category_id:
            categories = await bot_service.get_categories(db_user.id, parsed.type)
            
            if not categories:
                # No categories available, create without category
                transaction = await bot_service.create_transaction(
                    user_id=db_user.id,
                    transaction_type=parsed.type,
                    amount=parsed.amount,
                    description=parsed.description,
                    category_id=None,
                    raw_message=text,
                )
                
                type_emoji = "💸" if parsed.type == TransactionType.EXPENSE else "💰"
                safe_desc = parsed.description.replace('-', '\\-').replace('.', '\\.')
                response = (
                    f"✅ {type_emoji} Logged\\!\n\n"
                    f"Amount: \\${parsed.amount}\n"
                    f"Description: {safe_desc}\n"
                    f"Type: {parsed.type.value}\n"
                    f"⚠️ No category \\(run /start to load categories\\)"
                )
                await update.message.reply_text(response, parse_mode="MarkdownV2")
                return
            
            # Store transaction data for callback
            context.user_data['pending_transaction'] = {
                'type': parsed.type.value,
                'amount': str(parsed.amount),
                'description': parsed.description,
                'raw_message': text,
            }
            
            # Create inline keyboard (limit to 20 for better UX)
            keyboard = []
            for cat in categories[:20]:
                keyboard.append([
                    InlineKeyboardButton(
                        f"{cat.icon} {cat.name}",
                        callback_data=f"cat_{cat.id}"
                    )
                ])
            
            # Add "No category" option
            keyboard.append([
                InlineKeyboardButton("🚫 No category", callback_data="cat_none")
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            type_emoji = "💸" if parsed.type == TransactionType.EXPENSE else "💰"
            await update.message.reply_text(
                f"{type_emoji} Select category for:\n"
                f"${parsed.amount} - {parsed.description}",
                reply_markup=reply_markup,
            )
            return
        
        # Create transaction with auto-detected category
        transaction = await bot_service.create_transaction(
            user_id=db_user.id,
            transaction_type=parsed.type,
            amount=parsed.amount,
            description=parsed.description,
            category_id=category_id,
            raw_message=text,
        )
    
    # Send confirmation
    type_emoji = "💸" if parsed.type == TransactionType.EXPENSE else "💰"
    safe_desc = parsed.description.replace('-', '\\-').replace('.', '\\.')
    cat_name = matched_category.name if matched_category else "None"
    safe_cat = cat_name.replace('-', '\\-').replace('.', '\\.')
    
    response = (
        f"✅ {type_emoji} Logged\\!\n\n"
        f"Amount: \\${parsed.amount}\n"
        f"Description: {safe_desc}\n"
        f"Category: {safe_cat}"
    )
    
    await update.message.reply_text(response, parse_mode="MarkdownV2")


async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle category selection from inline keyboard."""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    callback_data = query.data
    
    # Get pending transaction data
    pending = context.user_data.get('pending_transaction')
    if not pending:
        await query.edit_message_text("❌ Transaction expired. Please try again.")
        return
    
    # Handle "no category" selection
    category_id = None
    if callback_data != "cat_none":
        category_id = callback_data.replace("cat_", "")
    
    # Create transaction
    async with async_session_maker() as session:
        bot_service = BotService(session)
        db_user = await bot_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
        )
        
        transaction = await bot_service.create_transaction(
            user_id=db_user.id,
            transaction_type=TransactionType(pending['type']),
            amount=Decimal(pending['amount']),
            description=pending['description'],
            category_id=category_id,
            raw_message=pending.get('raw_message'),
        )
    
    # Clear pending data
    context.user_data.pop('pending_transaction', None)
    
    # Send confirmation
    type_emoji = "💸" if pending['type'] == TransactionType.EXPENSE.value else "💰"
    await query.edit_message_text(
        f"✅ {type_emoji} Transaction saved!\n"
        f"${pending['amount']} - {pending['description']}"
    )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Exception while handling an update: {context.error}")


def create_application() -> Application:
    """Create and configure the bot application."""
    if not settings.telegram_bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment")
    
    # Create application
    application = Application.builder().token(settings.telegram_bot_token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("categories", categories_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
    # Add callback query handler for category selection
    application.add_handler(CallbackQueryHandler(category_callback, pattern=r"^cat_"))
    
    # Add message handler for regular text
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    logger.info("Bot application created successfully")
    return application


async def run_polling():
    """Run the bot with polling."""
    application = create_application()
    
    logger.info("Starting bot with polling...")
    
    # Run the application with polling
    async with application:
        await application.start()
        logger.info("✅ Bot is running! Press Ctrl+C to stop.")
        await application.updater.start_polling()
        
        # Keep running until interrupted
        import signal
        stop = asyncio.Event()
        
        def signal_handler(sig, frame):
            logger.info("Stopping bot...")
            stop.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        await stop.wait()


if __name__ == "__main__":
    import asyncio
    
    asyncio.run(run_polling())
