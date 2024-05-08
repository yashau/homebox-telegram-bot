#!/usr/bin/env python

import os
import json
import logging
import re
import asyncio
from asyncio.subprocess import create_subprocess_exec, PIPE
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv


load_dotenv()
bot_username = os.getenv("TELEGRAM_BOT_USERNAME")
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if bot_username in update.message.text:
        query = re.sub(bot_username, '', update.message.text).strip()
        if query:
            try:
                process = await create_subprocess_exec(
                    'python', 'query.py', query, stdout=PIPE, stderr=PIPE
                )
                stdout, stderr = await process.communicate()
                if stderr:
                    raise subprocess.CalledProcessError(stderr.decode())
                results = json.loads(stdout.decode())
                output = ""
                for index, result in enumerate(results, start=1):
                    name = result['name']
                    parent_locations = result['parent_locations']
                    location_chain = ' ➜ '.join([location['name'] for location in parent_locations[::-1]])
                    output += f"{index}. {name}\n{location_chain}\n"
                    if index != len(results):
                        output += "\n"
                if output:
                    await update.message.reply_text(output)
                else:
                    await update.message.reply_text("404 not found.")
            except Exception as e:
                logger.error(f"Error: {e}")


def main() -> None:
    application = Application.builder().token(bot_token).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
