from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from google_sheets import save_contractor_report, save_worker_report
import datetime
import os
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام، آماده‌ام که گزارش ثبت کنم.")

def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    # بقیه‌ی هندلرها رو اینجا اضافه کن

load_dotenv()

# مراحل گفتگو
(
    CHOOSING_REPORT_TYPE,
    GET_NAME,
    GET_JOB,
    GET_UNIT,
    GET_UNIT_PRICE,
    GET_QUANTITY,
    GET_WAGE,
    GET_OVERTIME,
) = range(8)

user_data = {}

reply_keyboard = [['کنترات', 'روزمزد']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "سلام! برای ثبت گزارش لطفاً نوع گزارش رو انتخاب کن:",
        reply_markup=markup
    )
    return CHOOSING_REPORT_TYPE

def choose_type(update: Update, context: CallbackContext):
    report_type = update.message.text
    user_data[update.effective_user.id] = {
        "type": report_type,
        "step": 0
    }
    update.message.reply_text("نام فرد را وارد کن:")
    return GET_NAME

def get_name(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id]["name"] = update.message.text
    update.message.reply_text("شغل یا کار انجام شده؟")
    return GET_JOB

def get_job(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id]["job"] = update.message.text

    if user_data[user_id]["type"] == "کنترات":
        update.message.reply_text("واحد کار (مثلاً متر، متر مربع،...)؟")
        return GET_UNIT
    else:
        update.message.reply_text("دستمزد پایه چقدره؟ (تومان)")
        return GET_WAGE

# مسیر کنترات:
def get_unit(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id]["unit"] = update.message.text
    update.message.reply_text("قیمت هر واحد چقدره؟")
    return GET_UNIT_PRICE

def get_unit_price(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id]["unit_price"] = update.message.text
    update.message.reply_text("تعداد واحد انجام شده؟")
    return GET_QUANTITY

def get_quantity(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id]["quantity"] = update.message.text

    data = user_data[user_id]
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    save_contractor_report(user_id, today, data["name"], data["job"], data["unit"], data["unit_price"], data["quantity"])

    update.message.reply_text("✅ گزارش کنترات ثبت شد. برای گزارش جدید /start رو بزن.")
    return ConversationHandler.END

# مسیر روزمزد:
def get_wage(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id]["wage"] = update.message.text
    update.message.reply_text("میزان اضافه‌کاری؟ (مثلاً 2 ساعت)")
    return GET_OVERTIME

def get_overtime(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_data[user_id]["overtime"] = update.message.text

    data = user_data[user_id]
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    save_worker_report(user_id, today, data["name"], data["job"], data["wage"], data["overtime"])

    update.message.reply_text("✅ گزارش روزمزد ثبت شد. برای گزارش جدید /start رو بزن.")
    return ConversationHandler.END

# کنسل کردن
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("⛔️ گزارش لغو شد. برای شروع مجدد /start رو بزن.")
    return ConversationHandler.END

def run_bot():
    updater = Updater(os.getenv("TELEGRAM_TOKEN"))
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_REPORT_TYPE: [MessageHandler(Filters.text & ~Filters.command, choose_type)],
            GET_NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            GET_JOB: [MessageHandler(Filters.text & ~Filters.command, get_job)],
            GET_UNIT: [MessageHandler(Filters.text & ~Filters.command, get_unit)],
            GET_UNIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, get_unit_price)],
            GET_QUANTITY: [MessageHandler(Filters.text & ~Filters.command, get_quantity)],
            GET_WAGE: [MessageHandler(Filters.text & ~Filters.command, get_wage)],
            GET_OVERTIME: [MessageHandler(Filters.text & ~Filters.command, get_overtime)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
