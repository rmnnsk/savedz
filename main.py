# import math
import telebot
from telebot import types
from config import bot_token, bot_dir
import sqlite3
import pendulum
import os


mode = "add"
is_logged = 1

class OSWorker:
    def __init__(self):
        week = ""

    def make_week(self, chat_id, shift = 0):
        today = pendulum.now()
        os.chdir(bot_dir + '/' + chat_id)
        today = today.add(days = 7 * shift)
        st = today.start_of('week')
        st_str = str(st.day)+'.'+ str(st.month)
        end = today.end_of('week')
        end_str = str(end.day) + '.' + str(end.month)
        self.week = st_str + '-' + end_str

        try:
            os.mkdir(self.week, 0o777)
        except OSError:
            return
        os.chdir(self.week)
        for day in range(1, 7):
            try:
                os.mkdir(str(day), 0o777)
            except:
                pass


bot = telebot.TeleBot(bot_token)
telebot.apihelper.proxy = {'https' : 'socks5://RSocks:RSforTG@telers5.rsocks.net:1490'}



main_markup_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard = True)
main_markup_keyboard.add("/add")
main_markup_keyboard.add("/get")

w = OSWorker()

@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        os.mkdir(bot_dir + '/' + str(message.chat.id))
    except:
        pass
    bot.send_message(message.chat.id, "Выбери команду: ", reply_markup = main_markup_keyboard)

@bot.message_handler(commands=['add', 'get'])
def get_week(message):
    global mode
    mode = message.text[1:]
    markup = types.ReplyKeyboardMarkup(selective = True, one_time_keyboard=True, row_width=3)
    markup.add("Текущая")
    markup.add("Следующая")
    msg = bot.reply_to(message, "Выбери неделю: ", reply_markup=markup)
    bot.register_next_step_handler(msg, get_day)

def get_day(message):
    sh = 0
    if (message.text == "Текущая"):
        sh = 0
    else:
        sh = 1
    w.make_week(str(message.chat.id), shift = sh)
    markup = types.ReplyKeyboardMarkup(selective = True, one_time_keyboard=True, row_width=3)
    buttons = []
    for i in range(1, 7):
        buttons.append(types.KeyboardButton(str(i)))
        if (i % 3 == 0):
            markup.row(buttons[0], buttons[1], buttons[2])
            buttons = []
    msg = bot.reply_to(message, "Выбери день: ", reply_markup=markup)
    bot.register_next_step_handler(msg, make_dir)

def make_dir(message):
    chat_id = message.chat.id
    os.chdir(bot_dir + '/' + str(chat_id) + '/' + w.week + '/' +  message.text)
    global mode
    if (mode == 'add'):
        msg = bot.reply_to(message, "Грузим фотку: ")
        bot.register_next_step_handler(msg, get_photo)
    else:
        send_photos(message)

def get_photo(message):
    try:

        chat_id = message.chat.id
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = file_info.file_path.split('/')[1];
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "Фото добавлено", reply_markup = main_markup_keyboard)
    except Exception as e:
        bot.reply_to(message, e)

def send_photos(message):
    try:
        chat_id = message.chat.id
        media = []
        files = os.listdir()
        print(files)
        for fl in files:
            media.append(types.InputMediaPhoto(open(fl, 'rb')))
        if (len(media) == 0):
            bot.send_message(chat_id, "Нет изображений", reply_markup = main_markup_keyboard)
        else:
            files = bot.send_media_group(chat_id, media)
    except Exception as e:
        bot.reply_to(message, e)

bot.polling()