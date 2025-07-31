from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
from sheets_handler import save_to_sheet
from datetime import datetime

TOKEN = "8338754838:AAH6WU34i0pqL9sGr-wFOv1sshQSKVyb6Z4"

ASK_REPORT_TYPE, FILL_DATA, CONFIRM_AGAIN = range(3)

user_data = {}

def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [["Contractor", "DailyWorker"]]
    update.message.reply_text(
        "سلام! لطفا نوع گزارش امروز رو انتخاب کن:", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_REPORT_TYPE

def ask_fields(update: Update, context: CallbackContext) -> int:
    report_type = update.message.text.lower()
    context.user_data["report_type"] = report_type
    context.user_data["telegram_id"] = update.effective_user.id
    context.user_data["date"] = datetime.now().strftime("%Y-%m-%d")

    update.message.reply_text("لطفا اطلاعات گزارش امروز رو به صورت زیر وارد کن:\n\n`ماده، مقدار، قیمت`")
    return FILL_DATA

def get_data(update: Update, context: CallbackContext) -> int:
    raw = update.message.text
    try:
        item, amount, price = raw.split(",")
        context.user_data["item"] = item.strip()
        context.user_data["amount"] = amount.strip()
        context.user_data["price"] = price.strip()
        save_to_sheet(context.user_data, context.user_data["report_type"])
        update.message.reply_text("✅ گزارش با موفقیت ثبت شد. گزارش دیگه‌ای هست؟ (بله / خیر)")
        return CONFIRM_AGAIN
    except Exception as e:
        update.message.reply_text("❌ فرمت اشتباهه. لطفا دوباره به صورت `ماده، مقدار، قیمت` وارد کن.")
        return FILL_DATA

def ask_another(update: Update, context: CallbackContext) -> int:
    if update.message.text.lower() == "بله":
        return start(update, context)
    update.message.reply_text("✅ ممنون! روز خوبی داشته باشید.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("گزارش لغو شد.")
    return ConversationHandler.END

