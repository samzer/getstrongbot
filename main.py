import telegram
import logging
import random
import os
import datetime

from decouple import config
from telegram.ext import Updater, CommandHandler

# Config variables
BOT_TOKEN = config('BOT_TOKEN')
DEBUG = config('DEBUG', default=False, cast=bool)

if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO
    
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def help(bot, update):
	update.message.reply_text("Help?!")


class GetStrongBot(object):
    def __init__(self):
        self.exercise_list = (
            "Pull Ups",
            "Push Up",
            "Squat",
            "Burpee",
            "Hand Stand Push Up",
            "Plank",
            "Sit-up",
            "Leg Raise",
            "Jack Knife",
            "Crunch",
            "Chin Up",
            "Plank Up",
            "Inchworm to Push-Up",
            "Dive Bomber Push-Up",
            "Tricep Dip",
        )

    def start(self, bot, update):
        result_exercises = self._sample_5_excercises()
        result_text = "Today's exercise list:\n"

        for i, exer in enumerate(result_exercises):
            result_text += f"{i+1}. {exer} \n"

        update.message.reply_text(result_text)

    def _sample_5_excercises(self):
        '''
		Return a list of 5 random exercises
        '''
        seed = self._get_day_seed()
        random.seed(seed)

        return random.sample(self.exercise_list, 5)

    def _get_day_seed(self):
        '''
		Get the day of the month to be used as a seed for random
        '''
        now = datetime.datetime.now()

        return now.day


updater = Updater(BOT_TOKEN)
getstrongbot = GetStrongBot()
updater.dispatcher.add_handler(CommandHandler('start', getstrongbot.start))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.start_polling()
updater.idle()
