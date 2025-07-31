from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram_handler import start, ask_fields, get_data, ask_another, cancel, ASK_REPORT_TYPE, FILL_DATA, CONFIRM_AGAIN

def run_bot():
    updater = Updater("8338754838:AAH6WU34i0pqL9sGr-wFOv1sshQSKVyb6Z4", use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_REPORT_TYPE: [MessageHandler(Filters.text & ~Filters.command, ask_fields)],
            FILL_DATA: [MessageHandler(Filters.text & ~Filters.command, get_data)],
            CONFIRM_AGAIN: [MessageHandler(Filters.text & ~Filters.command, ask_another)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    run_bot()

