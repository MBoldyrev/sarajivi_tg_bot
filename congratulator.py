import asyncio
import json
import logging
import pytz
import random

from datetime import datetime, time, timedelta

LAST_CONGRAT_DAY=None

CONGRATS_UNIMPORTANT_FACTOR = 0.4
CONGRATS_UNIMPORTANT = 'congrats_unimportant.json'

CONGRATS_IMPORTANT = 'congrats_important.json'

CHAT_ID = -1001238392515

CONGRAT_START_TIME=time(8,0,0)
CONGRAT_END_TIME=time(23,0,0)
CONGRAT_TZ=pytz.timezone('Europe/Moscow')

def _get_congrat_delay_sec():
    now = datetime.now(CONGRAT_TZ)
    today = datetime.now().date()
    start = datetime.combine(today, CONGRAT_START_TIME).replace(tzinfo=CONGRAT_TZ)
    end = datetime.combine(today, CONGRAT_END_TIME).replace(tzinfo=CONGRAT_TZ)
    if end < now:
        return None
    start = max(start, now)
    when = datetime.fromtimestamp(random.randint(int(start.timestamp()), int(end.timestamp()))).replace(tzinfo=CONGRAT_TZ)
    return (when - now).seconds

def _send_congrat(bot, text):
    logging.info(f"send congrat")
    if text['congrat']:
        bot.send_message(CHAT_ID, text['congrat'])

def _get_congrat_with_factor(filename, factor):
    if random.random() > factor:
        return None # lucky Sara
    congrats = _load_congrats_for_today(filename)
    if congrats:
        return random.choice(congrats)

def _load_congrats_for_today(filename):
    with open(filename, 'rt') as inp:
        return json.load(inp).get(datetime.today().date().strftime('%Y.%m.%d'))

def congrat(loop, bot):
    today = datetime.today().date()

    # avoid spamming on restart
    global LAST_CONGRAT_DAY
    if LAST_CONGRAT_DAY is None or LAST_CONGRAT_DAY == today:
        LAST_CONGRAT_DAY = today
        return

    LAST_CONGRAT_DAY = today

    congrat_for_today = \
        _get_congrat_with_factor(CONGRATS_IMPORTANT, 1.0) \
        or _get_congrat_with_factor(CONGRATS_UNIMPORTANT, CONGRATS_UNIMPORTANT_FACTOR)
    if congrat_for_today:
        delay = _get_congrat_delay_sec()
        logging.info(f"schedule congrat at {datetime.now() + timedelta(seconds=delay)}s")
        loop.call_later(delay, lambda: _send_congrat(bot, congrat_for_today))
