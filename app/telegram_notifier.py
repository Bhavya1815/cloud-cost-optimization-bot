import os
import asyncio

from telegram import Bot


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")

    if not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID is not configured.")

    bot = Bot(token=TELEGRAM_BOT_TOKEN)

    async with bot:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )


def send_message(message):
    asyncio.run(
        send_telegram_message(message)
    )


def send_weekly_report(report):
    """
    Send the generated weekly cost report
    to Telegram.
    """

    send_message(report)
