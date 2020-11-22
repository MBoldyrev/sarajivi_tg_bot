import itertools
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


def iter_words(msg: str):
    return re.findall(r"[а-яА-Я]+", msg)


def iter_words_filter_tag(msg: str, tag_props=set()):
    if not isinstance(tag_props, set):
        tag_props = set(tag_props)
    for word in iter_words(msg):
        morph_forms = MORPHER.parse(word)
        for morph_form in morph_forms:
            if tag_props in morph_form.tag:
                yield morph_form


def tags_from_1per_verbs(msg: str):
    for morph_form in iter_words_filter_tag(msg, ["VERB", "1per"]):
        yield morph_form.inflect({"impr"}).word


def tags_from_wish_verbs(msg: str):
    wish_words = ("хочу", "надо", "нужно", "хотела")
    for wish_word in wish_words:
        for after_wish_word in re.findall(
            r"(?<={})[^.?!]+".format(re.escape(wish_word)), msg
        ):
            for morph_form in iter_words_filter_tag(after_wish_word, ["INFN"]):
                yield morph_form.inflect({"impr"}).word


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def maybe_make_tag_reply(msg: str):
    # let's keep Sara's mind safe
    def sara_stay_safe(factor: float, generator):
        if random.random() > factor:
            return []  # lucky Sara
        return generator(msg)

    tags = list(
        itertools.chain(
            sara_stay_safe(0.1, tags_from_1per_verbs),
            sara_stay_safe(1.0, tags_from_wish_verbs),
        )
    )

    if tags:
        logging.debug(f"tags: {tags}")
        return "#сара{}".format(random.choice(tags))


def handle_sara_text_msg(update: Update, context: CallbackContext) -> None:
    maybe_tag = maybe_make_tag_reply(update.message.text)

    if maybe_tag is not None:
        update.message.reply_text(maybe_tag)


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
