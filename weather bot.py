# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib.request
import pandas as pd
import matplotlib
matplotlib.use('Gtk3Agg')
import matplotlib.pyplot as plt
import datetime
import threading
import telebot
from optparse import OptionParser


#Data parser
def parser_data():
    threading.Timer(3350.0, parser_data).start()
    html_doc = urllib.request.urlopen('http://www.meteoservice.ru/weather/detail/name/nizhniy+novgorod.html').read()
    soup = BeautifulSoup(html_doc)
    temperature_list = []
    time_list = []
    dictionary_data = {}
    title = soup.find('h1').text
    now = datetime.datetime.now()

    for table_data in soup.findAll('table', {"class": "data detail"}):

        for temperature in table_data.findAll('td', {"class": "temperature"}):
            temperature_element = temperature.text.rstrip().lstrip().replace('°', '')
            if temperature_element[0] == str('+'):
                temperature_list.append(int(temperature_element[1:]))
            else:
                temperature_list.append(int(temperature_element))

        for time in table_data.findAll('td', {"class": "time"}):
            time_list.append(time.text.replace(':', '.'))

    dictionary_data['temperature'] = temperature_list
    dictionary_data['time'] = time_list
    df = pd.DataFrame(dictionary_data)[:-1]
    df.plot(x='time', y='temperature', title='Weather for 24 hours', kind='barh', color='red', legend=True)
    #Save data in file
    df.to_csv('/home/andrey/data.csv', sep=',')

    #Save graph
    save_graph = plt.savefig('/home/andrey/out' + str(now.hour) + '.png', format='png')
    bot_my(df, now, title)

#Telegram Bot
def bot_my(df, now, title):
    bot = telebot.TeleBot('181479270:AAGvpYtoqhdmWWQhpksXygIjn_q6EMPR130')

#Send SMS
    parser = OptionParser()
    parser.add_option("-i", "--idsender", dest="idsender", default="673797DA-5739-EF3C-C3D8-B5A69EED9887",
                      help="ID user on sms.ru", metavar="IDSENDER")
    parser.add_option("-t", "--to", dest="to", default="79200642034", help="to telephone number", metavar="TO")
    parser.add_option("-s", "--subject", dest="subject", default="I'm Telegram bot. Use me: @zemlyanikin_bot", help="Name of subject", metavar="SUBJECT")
    (options, args) = parser.parse_args()
    sendsms(options.idsender, options.subject, options.to)
#Bot function
    @bot.message_handler(commands=['help'])
    def send_welcome(message):
        msg = bot.send_message(message.chat.id,
                               'Доступны команды:\n /start - запустить информер погоды.\n'
                               '/graph - получить график температуры на 24 часа.\n'
                               '/temperature_now - узнать температуру в данный момент.\n'
                               '/sheduler_temperature - получить расписание по часам.\n'
                               '/help - получить список команд управления.'
                               )

    @bot.message_handler(commands=['start'])
    def send_auth(message):
        msg = bot.send_message(message.chat.id,
                               'Привет! \nЯ твой информер погоды за окном :) \nДля тебя доступeн' + ' - ' + str(
                                   title) + '.\n'
                                            'Доступны команды:\n /start - запустить информер погоды.\n'
                                            '/graph - получить график температуры на 24 часа.\n'
                                            '/temperature_now - узнать температуру в данный момент.\n'
                                            '/sheduler_temperature - получить расписание по часам.\n'
                                            '/help - получить список команд управления.'
                               )

    @bot.message_handler(commands=['graph'])
    def sent_photo(message):
        msg = bot.send_photo(chat_id=message.chat.id, photo=open('/home/andrey/out' + str(now.hour) + '.png', 'rb'))
        msg = bot.send_message(message.chat.id, 'Доступны команды:\n /start - запустить информер погоды.\n'
                                                '/graph - получить график температуры на 24 часа.\n'
                                                '/temperature_now - узнать температуру в данный момент.\n'
                                                '/sheduler_temperature - получить расписание по часам.\n'
                                                '/help - получить список команд управления.'
                               )

    @bot.message_handler(commands=['sheduler_temperature'])
    def sent_document(message):
        msg = bot.send_document(chat_id=message.chat.id, data=open('/home/andrey/data.csv', 'rb'))
        msg = bot.send_message(message.chat.id, 'Доступны команды:\n /start - запустить информер погоды.\n'
                                                '/graph - получить график температуры на 24 часа.\n'
                                                '/temperature_now - узнать температуру в данный момент.\n'
                                                '/sheduler_temperature - получить расписание по часам.\n'
                                                '/help - получить список команд управления.'
                               )

    @bot.message_handler(commands=['temperature_now'])
    def send_temperature_now(message):
        now = datetime.datetime.now()
        date = now.strftime("%d-%m-%Y")
        time_now1 = now.strftime("%H:%M")
        time_now = str(str(now.hour) + str('.00'))
        index_element = df.time[df.time == time_now].index.tolist()
        row_temp = df[df['time'] == time_now]
        msg = bot.send_message(message.chat.id, 'Сегодня ' + str(date) + ' в ' + str(
            time_now1) + ' температура за окном составляет ' + str(row_temp['temperature'][index_element[0]]) + '°C.')
        msg = bot.send_message(message.chat.id, 'Доступны команды:\n /start - запустить информер погоды.\n'
                                                '/graph - получить график температуры на 24 часа.\n'
                                                '/temperature_now - узнать температуру в данный момент.\n'
                                                '/sheduler_temperature - получить расписание по часам.\n'
                                                '/help - получить список команд управления.'
                               )

    bot.polling()

#Send SMS function
def sendsms(idsender, subject, to):
    subject = subject.replace(" ", "+")
    url = "http://sms.ru/sms/send?api_id=%s&text=%s&to=%s" % (idsender, subject, to)
    res = urllib.request.urlopen(url)

if __name__ == "__main__":
    parser_data()