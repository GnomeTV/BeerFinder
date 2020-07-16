import telebot
import requests
import json
import API
import re
from telebot import types

bot = telebot.TeleBot(API.token)


@bot.message_handler(commands=['start'])
def help_com(message):
    start_key = types.ReplyKeyboardMarkup()
    start_key.row('Найти бар поблизости')
    start_key.row('Оставить отзыв', 'Поставить оценку бару')
    bot.send_message(message.from_user.id, "Выберите пункт", reply_markup=start_key)


@bot.message_handler(content_types=['text'])
def key_answer(message):
    if message.text == 'Найти бар поблизости':
        bot.send_message(message.chat.id, 'Не забудь ввести радиус поиска (в метрах)')

    elif re.match(r'\d{' + str(len(message.text)) + '}', message.text) != None:
        latitude = int(message.text) / (1000 * 111)
        longitude = int(message.text) / (1000 * 62.6)
        global part_of_requeuest
        part_of_requeuest = str(longitude) + ',' + str(latitude)
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_geo = types.KeyboardButton(text="И где же ты?", request_location=True)
        button_home = types.KeyboardButton(text="Главное меню")
        keyboard.add(button_geo)
        keyboard.add(button_home)
        bot.send_message(message.chat.id, 'Жду твое гео🗿', reply_markup=keyboard)
    elif message.text == 'Оставить отзыв':
        keyboard = types.InlineKeyboardMarkup()
        url_button = types.InlineKeyboardButton(text="Оставить отзыв в чате", url="https://t.me/beer_feedback")
        keyboard.add(url_button)
        bot.send_message(message.chat.id, "Чтобы оставить отзыв, просто ткни на кнопку!", reply_markup=keyboard)
    elif message.text == 'Поставить оценку бару' or message.text == 'Сорта пива':
        bot.send_message(message.chat.id, "Находится в разработке...")
        bot.send_message(message.chat.id, "Поддержи проект, чтобы мы перестали пить пиво и занялись проектом")
    elif message.text == 'Главное меню':
        start_key = types.ReplyKeyboardMarkup()
        start_key.row('Найти бар поблизости', 'Поставить оценку бару')
        start_key.row('Оставить отзыв')
        bot.send_message(message.from_user.id, "Выберите пункт", reply_markup=start_key)
    else:
        bot.send_message(message.chat.id, "Чел, не пори дичь. Го выпьем пивка 🍻")


@bot.message_handler(content_types=['location'])
def find_bar(message):
    if message.location is not None:
        start_key = types.ReplyKeyboardMarkup()
        start_key.row('Найти бар поблизости')
        start_key.row('Оставить отзыв', 'Поставить оценку бару')
        req = 'https://search-maps.yandex.ru/v1/?apikey=' + API.yand + '&text=бар&lang=ru_RU&ll=' + str(
            message.location.longitude) + ',' + str(message.location.latitude) + '&spn=' + part_of_requeuest + '&rspn=1'
        user_name = str(message.from_user.username)
        response = requests.get(req)
        js_bars = response.text
        js_bars = json.loads(js_bars)
        cord = str(message.location.latitude) + ',' + str(message.location.longitude)
        print(user_name)
        print(req)
        if js_bars['features'] != 0:
            for i in range(0, len(js_bars['features'])):
                bar_stat = ''
                bar_hours = ''
                bar_link = ''
                bar_category = ''
                bar_name = js_bars['features'][i]['properties']['name']
                bar_address = js_bars['features'][i]['properties']['CompanyMetaData']['address'] + ';'
                bar_stat = bar_name + '\n' + bar_address + '\n'
                try:
                    bar_hours = js_bars['features'][i]['properties']['CompanyMetaData']['Hours']['text']
                    bar_stat += bar_hours + '\n'
                except:
                    bar_hours = 'Часы работы не указаны'
                try:
                    bar_link = js_bars['features'][i]['properties']['CompanyMetaData']['url']
                    bar_stat += bar_link + '\n'
                except:
                    bar_link = 'Ссыка на сайт бара не указана'
                print('Перед котигориями i = ' + str(i))
                try:
                    for j in range(0, len(js_bars['features'][i]['properties']['CompanyMetaData']['Categories'])):
                        bar_category += js_bars['features'][i]['properties']['CompanyMetaData']['Categories'][j][
                                            'name'] + ';'
                    bar_stat += bar_category
                except:
                    bar_category = 'Категория у бара не указана'
                    bar_stat += bar_category

                bot.send_message(message.from_user.id, str(bar_stat))
                lat = js_bars['features'][i]['geometry']['coordinates'][1]
                lng = js_bars['features'][i]['geometry']['coordinates'][0]
                print(float(lat), ' , ', float(lng))
                bot.send_venue(message.chat.id, latitude=float(lat), longitude=float(lng), title=bar_name,
                               address=bar_address)
        else:
            bot.send_message(message.from_user.id, "Нет баров поблизости", reply_markup=start_key)
        bot.send_message(message.from_user.id, "Выберите пункт", reply_markup=start_key)


bot.polling(none_stop=True)
