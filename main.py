from telegram.ext import ApplicationBuilder
from telegram_handler import register_handlers

async def main():
    app = ApplicationBuilder().token("8338754838:AAH6WU34i0pqL9sGr-wFOv1sshQSKVyb6Z4").build()
    register_handlers(app)
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
