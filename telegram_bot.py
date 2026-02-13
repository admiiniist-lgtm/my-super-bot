import logging
import os
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- بخش وب‌سایت برای زنده نگه داشتن ربات در Render ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run_web():
    # Render به طور خودکار پورت را در متغیر PORT قرار می‌دهد
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()
# --------------------------------------------------

# تنظیمات لاگ برای مشاهده فعالیت‌ها در Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# مراحل گفتگو
NAME, GOAL_NAME, GOAL_MEASURE, GOAL_WHY, GOAL_OBSTACLES, HABIT_NAME, HABIT_MINIMAL, COMMITMENT, TIMING = range(9)

# توکن شما
TOKEN = "8490810340:AAE6YGC0RZzPLBC-Fr9HYU8SjTNiv6d6OVQ"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 سلام! من مربی هوشمند برنامه‌ریزی شما (گیوجی و نگین) هستم.\n\n"
        "خوشحالم که برای ساختن یک زندگی بهتر قدم برداشتی. بیا با هم یک برنامه شکست‌ناپذیر بسازیم!\n\n"
        "اول از همه، نام زیبای شما چیست؟"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"خوشبختم {update.message.text}! 😊\n\n"
        "🎯 **گام اول: تعریف هدف**\n"
        "هدفی که می‌خواهی در این دوره به آن برسی چیست؟ (فقط نام هدف را بنویس)\n\n"
        "💡 *مثال:* یادگیری زبان انگلیسی، کاهش وزن، مطالعه کتاب"
    )
    return GOAL_NAME

async def get_goal_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal_name'] = update.message.text
    await update.message.reply_text(
        "چطور می‌خواهی این هدف را اندازه بگیری؟ (عددی و دقیق بنویس)\n\n"
        "💡 *چطور پاسخ دهیم؟* هدفت باید قابل اندازه‌گیری باشد.\n"
        "✅ *مثال:* ۵ کیلو کاهش وزن، یادگیری ۵۰۰ لغت جدید، خواندن ۲۰ صفحه در روز"
    )
    return GOAL_MEASURE

async def get_goal_measure(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal_measure'] = update.message.text
    await update.message.reply_text(
        "چرا این هدف برایت مهم است؟ (دلیل قلبی‌ات را بنویس)\n\n"
        "💡 *چطور پاسخ دهیم؟* وقتی خسته شدی، این دلیل به تو انرژی می‌دهد."
    )
    return GOAL_WHY

async def get_goal_why(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal_why'] = update.message.text
    await update.message.reply_text(
        "فکر می‌کنی چه موانعی سر راهت باشد و چطور با آن‌ها روبرو می‌شوی؟\n\n"
        "💡 *مثال:* اگر بی‌حوصله بودم، فقط ۵ دقیقه انجامش می‌دهم."
    )
    return GOAL_OBSTACLES

async def get_goal_obstacles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['goal_obstacles'] = update.message.text
    await update.message.reply_text(
        "✨ **گام دوم: ساخت عادت**\n"
        "چه عادت کوچکی تو را به این هدف می‌رساند؟\n\n"
        "💡 *مثال:* روزی نیم ساعت ورزش، روزی ۱۰ لغت زبان"
    )
    return HABIT_NAME

async def get_habit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['habit_name'] = update.message.text
    await update.message.reply_text(
        "نسخه «خیلی کوچک» (مینیمال) این عادت چیست؟\n\n"
        "💡 *نکته:* این عادتی است که حتی در بدترین روزها هم بتوانی انجامش دهی.\n"
        "✅ *مثال:* فقط ۱ لغت، فقط ۱ دقیقه پیاده‌روی"
    )
    return HABIT_MINIMAL

async def get_habit_minimal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['habit_minimal'] = update.message.text
    await update.message.reply_text(
        "🤝 **گام سوم: تعهد**\n"
        "آیا متعهد می‌شوی که تحت هر شرایطی این برنامه را انجام دهی؟ (بنویس: بله متعهدم)"
    )
    return COMMITMENT

async def get_commitment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['commitment'] = update.message.text
    await update.message.reply_text(
        "📅 **گام آخر: زمان‌بندی**\n"
        "تا چه تاریخی می‌خواهی این هدف را دنبال کنی؟"
    )
    return TIMING

async def get_timing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    summary = (
        "🎉 **تبریک! برنامه شما آماده شد:**\n\n"
        f"👤 نام: {user_data['name']}\n"
        f"🎯 هدف: {user_data['goal_name']}\n"
        f"📏 معیار: {user_data['goal_measure']}\n"
        f"❤️ دلیل: {user_data['goal_why']}\n"
        f"🛡️ مقابله با موانع: {user_data['goal_obstacles']}\n"
        f"🔄 عادت: {user_data['habit_name']}\n"
        f"👶 نسخه کوچک: {user_data['habit_minimal']}\n"
        f"🤝 تعهد: {user_data['commitment']}\n"
        f"📅 تا تاریخ: {update.message.text}\n\n"
        "من در کنار شما هستم. موفق باشی! 🚀"
    )
    await update.message.reply_text(summary)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("برنامه متوقف شد. هر وقت خواستی دوباره شروع کنیم، /start را بزن.")
    return ConversationHandler.END

def main():
    # ۱. روشن کردن وب‌سایت در پس‌زمینه برای Render
    keep_alive()
    
    # ۲. اجرای ربات تلگرام
    application = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GOAL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal_name)],
            GOAL_MEASURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal_measure)],
            GOAL_WHY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal_why)],
            GOAL_OBSTACLES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal_obstacles)],
            HABIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_habit_name)],
            HABIT_MINIMAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_habit_minimal)],
            COMMITMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_commitment)],
            TIMING: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_timing)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    
    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
