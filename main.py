import telegram
import logging
import random
import os
import datetime
import yaml

from decouple import config
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from fuzzywuzzy import fuzz

# Config variables
BOT_TOKEN = config('BOT_TOKEN')
DEBUG = config('DEBUG', default=False, cast=bool)

if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=LOG_LEVEL)
logger = logging.getLogger(__name__)


def start(bot, update):
    update.message.reply_text("You can start by typing /help")

def help(bot, update):
	update.message.reply_text('''
Following are the list of commands:
1. /workout: Gives you the list of exercise for the day
                              ''')

class GetStrongBot(object):
    def __init__(self):
        self.data = self._load_data()

    def workout(self, bot, update):
        '''
        /workout handler
        '''
        chat_id = update.message.chat.id
        bot.send_message(chat_id=chat_id,
                             text="How many rounds?",
                             parse_mode=telegram.ParseMode.MARKDOWN,
                             reply_markup=self._round_keyboard_options())

    def workout_reply(self, bot, update):
        '''
        Reply message based on the workout menu selection
        '''
        query = update.callback_query
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        name = query.from_user.first_name
        rounds = query.data
        result_text = f'*{name}*, Your exercise,\nshould you choose to accept are:\n'
        result_exercises = self._sample_5_excercises(query.from_user.id)

        for i, exer in enumerate(result_exercises):
            logger.info(result_exercises)
            result_text += f"{i+1}. {exer} : {result_exercises[exer]['value']} \n"
        result_text+=f'\n*Total rounds: {rounds}*'

        bot.edit_message_text(chat_id = chat_id,
                             message_id = message_id,
                             text = result_text,
                             parse_mode = telegram.ParseMode.MARKDOWN,)

    def describe(self, bot, update, args):
        '''
        /describe handler
        '''
        chat_id = update.message.chat.id
        exercise_name = ""

        if len(args) > 0:
            exercise_name = " ".join(args)
            image_path = self._get_image_path(exercise_name)

            if image_path:
                bot.send_photo(chat_id=chat_id,
                                photo=open(image_path, 'rb'))
            else:
                bot.send_message(chat_id=chat_id,
                                text="Oops there is no exercise with this name",
                                parse_mode=telegram.ParseMode.MARKDOWN,)
        else:
            bot.send_message(chat_id=chat_id,
                             text="Please give an exercise name in the format '/describe <name>'",
                             parse_mode=telegram.ParseMode.MARKDOWN,)

    def _get_image_path(self, name):
        '''
        Get the image path of the name using fuzzy match
        '''
        result = None
        similarity_ratio = 0

        for category in self.data:
            for e in self.data[category]:
                ename = list(e.keys())[0]
                current_ratio = fuzz.ratio(name.lower(), ename.lower())
                if current_ratio > similarity_ratio:
                    result = e[ename]['file']
                    similarity_ratio = current_ratio

        if similarity_ratio < 90:
            return None

        return result


    def _sample_5_excercises(self, chat_id):
        '''
		Return a list of 5 random exercises
        '''
        seed = self._get_day_seed()
        random.seed(seed + chat_id)

        # shuffle the list to select randomly
        # from upper, core and leg
        selection_list = [2,2,1]
        random.shuffle(selection_list)

        # Sample from each category
        upper = random.sample(self.data['Upper'], selection_list[0])
        core = random.sample(self.data['Core'], selection_list[1])
        leg = random.sample(self.data['Leg'], selection_list[2])

        # Combine the dicts
        result = {}
        for d in (upper + core + leg):
            result.update(d)

        return result

    def _get_day_seed(self):
        '''
		Get the day of the month to be used as a seed for random
        '''
        now = datetime.datetime.now()

        return now.day

    def _load_data(self):
        with open('exercise.yaml') as f:
            data = yaml.safe_load(f)

        return data

    def _round_keyboard_options(self):
        '''
        Number of rounds menu for /workout
        '''
        keyboard = [[InlineKeyboardButton('1', callback_data='1')],
                    [InlineKeyboardButton('2', callback_data='2')],
                  [InlineKeyboardButton('3', callback_data='3')],
                  [InlineKeyboardButton('4', callback_data='4')],
                  [InlineKeyboardButton('5', callback_data='5')],
                  [InlineKeyboardButton('6', callback_data='6')]]

        return InlineKeyboardMarkup(keyboard)


updater = Updater(BOT_TOKEN)
getstrongbot = GetStrongBot()
updater.dispatcher.add_handler(CommandHandler('workout', getstrongbot.workout))
updater.dispatcher.add_handler(CallbackQueryHandler(getstrongbot.workout_reply, pattern='[1-6]'))
updater.dispatcher.add_handler(CommandHandler('help', help))
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('describe', getstrongbot.describe, pass_args=True))
updater.start_polling()
updater.idle()
