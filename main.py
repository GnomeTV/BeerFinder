import telebot
import requests
import json
import re
from telebot import types
import os

token = os.environ.get("TOKEN",)
api_google = os.environ.get("API_GOOGLE",)
bot = telebot.TeleBot(token)
glob_req = None
cord = None


@bot.message_handler(commands=['start'])
def help_com(message):
    start_key = types.ReplyKeyboardMarkup()
    start_key.row('Rating Beer')
    start_key.row('Find Bar')
    bot.send_message(message.from_user.id, "Выберите пункт", reply_markup=start_key)


@bot.message_handler(content_types=['text'])
def key_answ(message):
    if message.text == 'Find Bar':
        bot.send_message(message.chat.id, "Желаемый радиус поиска (в метрах)")
    else:
        global rad
        rad = message.text
        if re.match('\d'+'{'+str(len(message.text))+'}', rad) != None:
            keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
            keyboard.add(button_geo)
            bot.send_message(message.chat.id, 'Отправь геолокацию, посмотреть ближайшие бары в радиусе ' + rad +'м',
                             reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, "Ошибка, попробуйте снова")
        print(rad)


@bot.message_handler(content_types=['location'])
def find_bar(message):
    if message.location is not None:
        start_key = types.ReplyKeyboardMarkup()
        start_key.row('Rating Beer')
        start_key.row('Find Bar')
        req = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + str(
            message.location.latitude) + ',' + str(
            message.location.longitude) + '&radius='+rad+'&type=bar&key=' + api_google
        response = requests.get(req)
        js_bars = response.text
        js_bars = json.loads(js_bars)
        # js_user = str(message.location)
        # print(js_user)
        # print(type(js_user))
        # js_us = json.loads(js_user)
        # print(js_us)
        cord = str(message.location.latitude) + ',' + str(message.location.longitude)
        print(req)
        if js_bars['results'] != None:
            for i in range(0, len(js_bars['results'])):
                lat = js_bars['results'][i]['geometry']['location']['lat']
                lng = js_bars['results'][i]['geometry']['location']['lng']
                bar_name = js_bars['results'][i]['name']
                bot.send_message(message.from_user.id, str(bar_name))
                try:
                    rating = js_bars['results'][i]['rating']
                    bot.send_message(message.from_user.id, 'Рейтинг: ' + str(rating))
                except:
                    bot.send_message(message.from_user.id, 'Рейтинг: ' + '-')
                bot.send_location(message.from_user.id, latitude=float(lat), longitude=float(lng))
        elif js_bars['status'] == 'OVER_QUERY_LIMIT':
            bot.send_message(message.from_user.id, "Превышен лимит запросов, попробуйте снова через 20 секунд",
                             reply_markup=start_key)
        elif js_bars['status'] == 'ZERO_RESULTS':
            bot.send_message(message.from_user.id, "Нет баров поблизости",
                             reply_markup=start_key)
        bot.send_message(message.from_user.id, "Выберите пункт", reply_markup=start_key)


bot.polling(none_stop=True)
