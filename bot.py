import json
import logging
import pymorphy2
import random
import re

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

MORPHER = pymorphy2.MorphAnalyzer()

with open("secrets", "rb") as inp:
    SETTINGS = json.load(inp)


def gen_tags(msg: str):
    for word in re.findall(r"[а-яА-Я]+", msg):
        morph_forms = MORPHER.parse(word)
        for morph_form in morph_forms:
            if morph_form.tag.POS == "VERB" and morph_form.tag.person == "1per":
                yield "#сара{}".format(morph_form.inflect({"impr"}).word)


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def handle_sara_text_msg(update: Update, context: CallbackContext) -> None:
    tags = list(gen_tags(update.message.text))
    if tags:
        logging.debug(f"tags: {tags}")
        update.message.reply_text(random.choice(tags))


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(SETTINGS["TelegramApi"], use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        MessageHandler(
            Filters.text & ~Filters.command & Filters.user(username="liralemur"),
            handle_sara_text_msg,
        )
    )

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
