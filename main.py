import logging
import datetime
import gspread
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)
from oauth2client.service_account import ServiceAccountCredentials

# اتصال به گوگل شیت
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1LM6Pbihi_gbFHHfLdYdVZiTRsNMRDM-TnCjEwJobLIg/edit").sheet1

# مراحل گفت‌وگو
ASK_IF_REPORT, REPORT_TYPE, GET_NAME, GET_FIELD, GET_UNIT, GET_PRICE, GET_AMOUNT, CONFIRM_AGAIN, \
GET_DAILY_PAY, GET_OVERTIME = range(10)

# ذخیره موقت اطلاعات کاربران
user_data_dict = {}

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! آیا امروز گزارشی داری؟", reply_markup=ReplyKeyboardMarkup([["بله", "خیر"]], one_time_keyboard=True))
    return ASK_IF_REPORT

# پاسخ به سوال اولیه
async def ask_if_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "خیر":
        await update.message.reply_text("باشه، تا فردا!")
        return ConversationHandler.END
    else:
        await update.message.reply_text("نوع گزارش رو انتخاب کن:", reply_markup=ReplyKeyboardMarkup([["کنترات", "روزمزد"]], one_time_keyboard=True))
        return REPORT_TYPE

# انتخاب نوع گزارش
async def report_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = {"report_type": update.message.text}
    user_data_dict[update.effective_chat.id] = user_data

    if update.message.text == "کنترات":
        await update.message.reply_text("نام فرد رو وارد کن:")
        return GET_NAME
    else:
        await update.message.reply_text("نام روزمزد رو وارد کن:")
        return GET_NAME

# دریافت اطلاعات پله به پله
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_dict[update.effective_chat.id]["name"] = update.message.text
    await update.message.reply_text("زمینه کاری:")
    return GET_FIELD

async def get_field(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_dict[update.effective_chat.id]["field"] = update.message.text
    if user_data_dict[update.effective_chat.id]["report_type"] == "کنترات":
        await update.message.reply_text("واحد اندازه‌گیری:", reply_markup=ReplyKeyboardMarkup([["متر", "مترمربع", "واحد"]], one_time_keyboard=True))
        return GET_UNIT
    else:
        await update.message.reply_text("مزد روزمزد را وارد کن:")
        return GET_DAILY_PAY

async def get_unit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_dict[update.effective_chat.id]["unit"] = update.message.text
    await update.message.reply_text("قیمت واحد:")
    return GET_PRICE

async def get_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_dict[update.effective_chat.id]["unit_price"] = update.message.text
    await update.message.reply_text("تعداد:")
    return GET_AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = user_data_dict[update.effective_chat.id]
    user_data["amount"] = update.message.text
    user_data["total_price"] = str(float(user_data["unit_price"]) * float(user_data["amount"]))
    user_data["date"] = str(datetime.date.today())
    user_data["user_id"] = update.effective_chat.id

    try:
        sheet.append_row([
            user_data["date"],
            user_data["user_id"],
            user_data["report_type"],
            user_data["name"],
            user_data["field"],
            user_data.get("unit", ""),
            user_data.get("unit_price", ""),
            user_data.get("amount", ""),
            user_data.get("total_price", ""),
        ])
        await update.message.reply_text("✅ با موفقیت ثبت شد. مایل به ثبت گزارش جدیدی هستی؟", reply_markup=ReplyKeyboardMarkup([["پایان", "ثبت مجدد"]], one_time_keyboard=True))
        return CONFIRM_AGAIN
    except Exception as e:
        await update.message.reply_text("❌ خطا در ثبت گزارش. لطفا دوباره امتحان کن.")
        return REPORT_TYPE

async def get_daily_pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data_dict[update.effective_chat.id]["daily_pay"] = update.message.text
    await update.message.reply_text("آیا اضافه کار داشته؟", reply_markup=ReplyKeyboardMarkup([["بله", "خیر"]], one_time_keyboard=True))
    return GET_OVERTIME

async def get_overtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = user_data_dict[update.effective_chat.id]
    user_data["overtime"] = update.message.text
    user_data["date"] = str(datetime.date.today())
    user_data["user_id"] = update.effective_chat.id

    try:
        sheet.append_row([
            user_data["date"],
            user_data["user_id"],
            user_data["report_type"],
            user_data["name"],
            user_data["field"],
            "",
            user_data["daily_pay"],
            user_data["overtime"],
            "",
        ])
        await update.message.reply_text("✅ با موفقیت ثبت شد. مایل به ثبت گزارش جدیدی هستی؟", reply_markup=ReplyKeyboardMarkup([["پایان", "ثبت مجدد"]], one_time_keyboard=True))
        return CONFIRM_AGAIN
    except:
        await update.message.reply_text("❌ ثبت نشد. دوباره امتحان کن.")
        return REPORT_TYPE

async def confirm_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "پایان":
        await update.message.reply_text("ممنون، موفق باشی!")
        return ConversationHandler.END
    else:
        await update.message.reply_text("نوع گزارش رو انتخاب کن:", reply_markup=ReplyKeyboardMarkup([["کنترات", "روزمزد"]], one_time_keyboard=True))
        return REPORT_TYPE

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token("8338754838:AAH6WU34i0pqL9sGr-wFOv1sshQSKVyb6Z4").build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_IF_REPORT: [MessageHandler(filters.TEXT, ask_if_report)],
            REPORT_TYPE: [MessageHandler(filters.TEXT, report_type)],
            GET_NAME: [MessageHandler(filters.TEXT, get_name)],
            GET_FIELD: [MessageHandler(filters.TEXT, get_field)],
            GET_UNIT: [MessageHandler(filters.TEXT, get_unit)],
            GET_PRICE: [MessageHandler(filters.TEXT, get_price)],
            GET_AMOUNT: [MessageHandler(filters.TEXT, get_amount)],
            GET_DAILY_PAY: [MessageHandler(filters.TEXT, get_daily_pay)],
            GET_OVERTIME: [MessageHandler(filters.TEXT, get_overtime)],
            CONFIRM_AGAIN: [MessageHandler(filters.TEXT, confirm_again)],
        },
        fallbacks=[]
    )

    app.add_handler(conv)
    app.run_polling()
