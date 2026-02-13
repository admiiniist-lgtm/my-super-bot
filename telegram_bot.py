import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define conversation states
NAME, GOAL_WHAT, GOAL_WHY, GOAL_METRIC, GOAL_OBSTACLES, HABIT_BEHAVIOR, HABIT_WHEN, HABIT_MINIMAL, HABIT_MEASURE, HABIT_TRIAL, HABIT_REWARD, ANALYZE_MEANING, ANALYZE_SOLUTION, ANALYZE_DECISION = range(14)

# Dictionary to store user data temporarily
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user for their name."""
    user = update.effective_user
    await update.message.reply_html(
        f"سلام {user.mention_html()}! به ربات برنامه‌ریزی و ساخت عادت خوش آمدید. من به شما کمک می‌کنم تا اهداف خود را به صورت دقیق مشخص کرده و عادات موثری برای رسیدن به آن‌ها بسازید. برای شروع، نام خود را وارد کنید.",
        reply_markup=ForceReply(selective=True),
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the user's name and asks the first goal question."""
    user = update.effective_user
    user_data[user.id] = {"name": update.message.text}
    logger.info("User %s entered name: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "خیلی خب، {}. حالا بیایید اولین هدف خود را تعریف کنیم.\n\n"\
        "**سوال ۱: دقیقاً چه می‌خواهم؟**\n"\
        "*راهنما:* هدف باید کاملاً مشخص، قابل اندازه‌گیری و دارای بازه زمانی باشد. از فرمول زیر استفاده کنید.\n"\
        "*قالب پاسخ:* `تا تاریخ [تاریخ دقیق] می‌خواهم [نتیجه مشخص و قابل سنجش].`\n"\
        "*مثال:* `تا تاریخ ۳۱ شهریور ۱۴۰۳ می‌خواهم وزنم را به ۷۵ کیلوگرم برسانم.` یا `تا پایان سال جاری، می‌خواهم یک کتاب ۵۰ صفحه‌ای بنویسم.`".format(user_data[user.id]["name"])
    )
    return GOAL_WHAT

async def get_goal_what(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the goal and asks the second goal question."""
    user = update.effective_user
    user_data[user.id]["goal_what"] = update.message.text
    logger.info("User %s entered goal_what: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "**سوال ۲: چرا این هدف برای من مهم است؟**\n"\
        "*راهنما:* دلایل احساسی و منطقی خود را بنویسید. این دلایل، انگیزه شما در روزهای سخت خواهند بود.\n"\
        "*قالب پاسخ:* `این هدف برای من مهم است چون [ارزش/حسی که می‌خواهم تجربه کنم] و این با [ارزش شخصی] من هم‌سو است.`\n"\
        "*مثال:* `چون می‌خواهم احساس سلامتی و انرژی بیشتری داشته باشم و این با ارزش سلامتی و تناسب اندام من هم‌سو است.`\n"\
        "*نکات شخصی‌سازی:* ۱ تا ۳ دلیل احساسی و منطقی بنویسید. قوی‌ترین دلیل را ستاره بزنید."
    )
    return GOAL_WHY

async def get_goal_why(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the reason for the goal and asks the third goal question."""
    user = update.effective_user
    user_data[user.id]["goal_why"] = update.message.text
    logger.info("User %s entered goal_why: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "**سوال ۳: از کجا معلوم می‌فهمم موفق شدم؟ (معیار موفقیت)**\n"\
        "*راهنما:* معیار موفقیت باید دقیق، عددی و قابل اندازه‌گیری باشد. ابزار اندازه‌گیری خود را نیز مشخص کنید.\n"\
        "*قالب پاسخ:* `وقتی [معیار دقیق و عددی] را دیدم، می‌فهمم موفق شدم.`\n"\
        "*مثال:* `وقتی عدد ۷۵ کیلوگرم را روی ترازو دیدم.` یا `وقتی ۵۰ صفحه از کتابم را تکمیل کردم.`\n"\
        "*نکات شخصی‌سازی:* Daily/Weekly metric، ابزار اندازه‌گیری (اپ، دفتر، عکس) را مشخص کنید."
    )
    return GOAL_METRIC

async def get_goal_metric(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the goal metric and asks the fourth goal question."""
    user = update.effective_user
    user_data[user.id]["goal_metric"] = update.message.text
    logger.info("User %s entered goal_metric: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "**سوال ۴: کدام موانع احتمالی هستند؟**\n"\
        "*راهنما:* ۳ مانع احتمالی را شناسایی کرده و برای هر کدام یک راه‌حل ساده ارائه دهید. به یاد داشته باشید، راه‌حل مانع شماره ۱ را باید امروز اجرا کنید.\n"\
        "*قالب پاسخ:* `موانع احتمالی:\n"\
        "    ۱. [مانع اول]: [راه‌حل ساده]\n"\
        "    ۲. [مانع دوم]: [راه‌حل ساده]\n"\
        "    ۳. [مانع سوم]: [راه‌حل ساده]`\n"\
        "*مثال:* `۱. کمبود وقت: هر روز ۱۵ دقیقه زودتر بیدار شوم و ورزش کنم.\n"\
        "    ۲. خستگی بعد از کار: برنامه ورزشی را به صبح منتقل کنم.\n"\
        "    ۳. عدم انگیزه: با یک دوست برای ورزش قرار بگذارم.`"
    )
    return GOAL_OBSTACLES

async def get_goal_obstacles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the goal obstacles and moves to habit design."""
    user = update.effective_user
    user_data[user.id]["goal_obstacles"] = update.message.text
    logger.info("User %s entered goal_obstacles: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "عالی! حالا که هدف شما مشخص شد، بیایید عادات موثری برای رسیدن به آن طراحی کنیم.\n\n"\
        "**سوال ۱: کدام رفتارِ کوچک، بیشترین اثر را دارد؟**\n"\
        "*راهنما:* به رفتاری فکر کنید که با کمترین انرژی، بیشترین تاثیر را در رسیدن به هدف شما دارد. این رفتار باید شکست‌ناپذیر باشد.\n"\
        "*قالب پاسخ:* `اگر روزی [فعل کوچک] را انجام دهم، احتمال رسیدنم به هدف X افزایش می‌یابد.`\n"\
        "*مثال:* `اگر روزی ۵ دقیقه پیاده‌روی کنم، احتمال رسیدنم به هدف کاهش وزن افزایش می‌یابد.`\n"\
        "*نکات شخصی‌سازی:* به انرژی، زمان، مکان و تعاملات اجتماعی خود فکر کنید."
    )
    return HABIT_BEHAVIOR

async def get_habit_behavior(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the habit behavior and asks the second habit question."""
    user = update.effective_user
    user_data[user.id]["habit_behavior"] = update.message.text
    logger.info("User %s entered habit_behavior: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "**سوال ۲: در چه زمان/مکانی /بعد از چه چیزی آن را انجام دهم؟ (آنگاه-اگر)**\n"\
        "*راهنما:* یک \"انکر\" (لنگر) طبیعی در روز خود پیدا کنید که عادت جدید را به آن وصل کنید. این کار به شما کمک می‌کند تا عادت را فراموش نکنید.\n"\
        "*قالب پاسخ:* `اگر [مرکز/رویداد روزانه] اتفاق افتاد، آنگاه [عادت] را انجام می‌دهم.`\n"\
        "*مثال:* `اگر بعد از صبحانه، آنگاه ۲ دقیقه تنفس عمیق + ۱ صفحه مطالعه.`\n"\
        "*نکات شخصی‌سازی:* یک \"انکر\" طبیعی روزانه پیدا کنید."
    )
    return HABIT_WHEN

async def get_habit_when(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the habit timing and asks the third habit question."""
    user = update.effective_user
    user_data[user.id]["habit_when"] = update.message.text
    logger.info("User %s entered habit_when: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "**سوال ۳: نسخهٔ مینیمالِ شکست‌ناپذیر چیست؟**\n"\
        "*راهنما:* کوچکترین و آسان‌ترین نسخه از عادت خود را تعریف کنید که انجام آن تقریباً غیرممکن باشد. این نسخه باید \"شکست‌ناپذیر\" باشد.\n"\
        "*قالب پاسخ:* `کمترین کاری که هر روز باید انجام دهم: [مثلاً ۱ دقیقه، ۱ تکرار، ۱ عکس].`\n"\
        "*مثال:* `کمترین کاری که هر روز باید انجام دهم: ۱ دقیقه دویدن.`\n"\
        "*نکته مهم:* اگر هر روز این نسخه مینیمال انجام شود، بعداً می‌توان آن را افزایش داد."
    )
    return HABIT_MINIMAL

async def get_habit_minimal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the minimal habit and asks the fourth habit question."""
    user = update.effective_user
    user_data[user.id]["habit_minimal"] = update.message.text
    logger.info("User %s entered habit_minimal: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "**سوال ۴: چطور اندازه‌گیری کنم؟ (ساده و پایدار)**\n"\
        "*راهنما:* روش اندازه‌گیری عادت خود را ساده و پایدار انتخاب کنید. این کار به شما کمک می‌کند تا پیشرفت خود را رصد کنید.\n"\
        "*قالب پاسخ:* `روزانه/هفته‌ای این عدد را ثبت می‌کنم: [عدد/تیک/عکس].`\n"\
        "*مثال:* `روزانه تیک می‌زنم که آیا ۱ دقیقه دویدم یا نه.`\n"\
        "*ابزار:* تقویم دیواری، اپ habit tracker، دفترچه ساده."
    )
    return HABIT_MEASURE

async def get_habit_measure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the habit measurement and asks the fifth habit question."""
    user = update.effective_user
    user_data[user.id]["habit_measure"] = update.message.text
    logger.info("User %s entered habit_measure: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "**سوال ۵: آزمایش/دورهٔ امتحان چقدر باشد؟**\n"\
        "*راهنما:* یک دوره آزمایشی برای عادت خود تعیین کنید و معیار موفقیت را مشخص کنید.\n"\
        "*قالب پاسخ:* `آزمایش [تعداد روز] روزه با معیار موفقیت X (مثلاً >=۸۰% روزها).`\n"\
        "*مثال:* `آزمایش ۲۱ روزه با معیار موفقیت: حداقل ۱۵ روز انجام شده.`\n"\
        "*نکته:* ۱۴ روز برای کوچک‌ترین عادات، ۳۰–۹۰ روز برای عادات پیچیده‌تر."
    )
    return HABIT_TRIAL

async def get_habit_trial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the habit trial period and asks the sixth habit question."""
    user = update.effective_user
    user_data[user.id]["habit_trial"] = update.message.text
    logger.info("User %s entered habit_trial: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "**سوال ۶: پاداش فوری چیست؟**\n"\
        "*راهنما:* یک پاداش کوچک و فوری برای خودتان در نظر بگیرید که بلافاصله بعد از انجام عادت، آن را دریافت کنید. این کار به مغز شما کمک می‌کند تا عادت را با حس خوب مرتبط کند.\n"\
        "*قالب پاسخ:* `بعد از انجام عادت، پاداشِ فوریِ ساده: [چیز لذت‌بخش کوتاه‌مدت].`\n"\
        "*مثال:* `بعد از انجام عادت، پاداشِ فوریِ ساده: ۵ دقیقه بازی، یک قهوهٔ خوب، یا نمره شخصی.`"
    )
    return HABIT_REWARD

async def get_habit_reward(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the habit reward and moves to the analysis phase."""
    user = update.effective_user
    user_data[user.id]["habit_reward"] = update.message.text
    logger.info("User %s entered habit_reward: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "بسیار عالی! شما با موفقیت هدف و عادت خود را تعریف کردید. حالا بیایید یاد بگیریم چطور پاسخ‌های خود را تحلیل و بهینه‌سازی کنیم.\n\n"\
        "**سوال ۱: تجزیه و تحلیل کوتاه (۱-۲ خط): چه معنا دارد؟**\n"\
        "*راهنما:* بعد از ثبت هر پاسخ، یک تحلیل کوتاه از آن ارائه دهید. این تحلیل به شما کمک می‌کند تا الگوها را شناسایی کنید.\n"\
        "*مثال:* `گزارش امروز: ۴ از ۷. معنی: شروع خوب اما عصرها انرژی کم می‌شود.`"
    )
    return ANALYZE_MEANING

async def get_analyze_meaning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the analysis meaning and asks for a solution."""
    user = update.effective_user
    user_data[user.id]["analyze_meaning"] = update.message.text
    logger.info("User %s entered analyze_meaning: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "**سوال ۲: راه‌حل/آزمایش پیشنهادی (همیشه یک کار کوچک):**\n"\
        "*راهنما:* یک راه‌حل یا آزمایش کوچک برای بهبود وضعیت پیشنهاد دهید. این آزمایش باید قابل اجرا و مشخص باشد.\n"\
        "*مثال:* `آزمایش: عادت را به صبح منتقل کن و فقط ۵ دقیقه انجام بده تا ببینیم اثر دارد یا نه.`"
    )
    return ANALYZE_SOLUTION

async def get_analyze_solution(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the proposed solution and asks for a decision criterion."""
    user = update.effective_user
    user_data[user.id]["analyze_solution"] = update.message.text
    logger.info("User %s entered analyze_solution: %s", user.first_name, update.message.text)

    await update.message.reply_text(
        "**سوال ۳: معیار تصمیم‌گیری: آیا تغییر دائمی، تغییر آزمایشی یا ادامه بدهیم؟**\n"\
        "*راهنما:* بر اساس نتایج، تصمیم بگیرید که آیا تغییر دائمی اعمال کنید، تغییر را به صورت آزمایشی ادامه دهید یا برنامه فعلی را حفظ کنید.\n"\
        "*قالب تصمیم:* `اگر در ۷ روز آینده میانگین ≥۸۰% شد: نگه‌دار؛ اگر <۵۰%: تغییر زمان/اندازه یا حذف.`"
    )
    return ANALYZE_DECISION

async def get_analyze_decision(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the decision criterion and ends the conversation for now, displaying all collected data."""
    user = update.effective_user
    user_data[user.id]["analyze_decision"] = update.message.text
    logger.info("User %s entered analyze_decision: %s", user.first_name, update.message.text)

    # Generate a summary of the collected data
    summary = "**خلاصه اطلاعات شما:**\n\n"
    summary += f"**نام:** {user_data[user.id].get('name', 'نامشخص')}\n"
    summary += f"**هدف (چه می‌خواهم):** {user_data[user.id].get('goal_what', 'نامشخص')}\n"
    summary += f"**چرا مهم است:** {user_data[user.id].get('goal_why', 'نامشخص')}\n"
    summary += f"**معیار موفقیت:** {user_data[user.id].get('goal_metric', 'نامشخص')}\n"
    summary += f"**موانع احتمالی:** {user_data[user.id].get('goal_obstacles', 'نامشخص')}\n\n"
    summary += f"**رفتار عادت:** {user_data[user.id].get('habit_behavior', 'نامشخص')}\n"
    summary += f"**زمان/مکان عادت:** {user_data[user.id].get('habit_when', 'نامشخص')}\n"
    summary += f"**نسخه مینیمال عادت:** {user_data[user.id].get('habit_minimal', 'نامشخص')}\n"
    summary += f"**نحوه اندازه‌گیری عادت:** {user_data[user.id].get('habit_measure', 'نامشخص')}\n"
    summary += f"**دوره آزمایش عادت:** {user_data[user.id].get('habit_trial', 'نامشخص')}\n"
    summary += f"**پاداش فوری عادت:** {user_data[user.id].get('habit_reward', 'نامشخص')}\n\n"
    summary += f"**تحلیل معنی:** {user_data[user.id].get('analyze_meaning', 'نامشخص')}\n"
    summary += f"**راه‌حل پیشنهادی:** {user_data[user.id].get('analyze_solution', 'نامشخص')}\n"
    summary += f"**معیار تصمیم‌گیری:** {user_data[user.id].get('analyze_decision', 'نامشخص')}\n\n"
    summary += "از اینکه از ربات ما استفاده کردید متشکریم!" # Add a thank you message

    await update.message.reply_text(summary, parse_mode='Markdown')

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.effective_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "مکالمه لغو شد. امیدوارم در آینده بتوانم به شما کمک کنم."
    )
    user_data.pop(user.id, None) # Clear user data on cancel
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token obtained from BotFather
    application = Application.builder().token("8490810340:AAE6YGC0RZzPLBC-Fr9HYU8SjTNiv6d6OVQ").build()

    # Add conversation handler with states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GOAL_WHAT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal_what)],
            GOAL_WHY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal_why)],
            GOAL_METRIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal_metric)],
            GOAL_OBSTACLES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goal_obstacles)],
            HABIT_BEHAVIOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_habit_behavior)],
            HABIT_WHEN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_habit_when)],
            HABIT_MINIMAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_habit_minimal)],
            HABIT_MEASURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_habit_measure)],
            HABIT_TRIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_habit_trial)],
            HABIT_REWARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_habit_reward)],
            ANALYZE_MEANING: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_analyze_meaning)],
            ANALYZE_SOLUTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_analyze_solution)],
            ANALYZE_DECISION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_analyze_decision)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
      main()
