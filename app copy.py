#!flask/bin/python
#from urllib.parse import uses_relative
from flask import Flask, jsonify, abort, make_response, request, json, send_from_directory
import telebot
#from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from requests import get
import src.modules # импорт нашего модуля 
from dotenv import load_dotenv
import os
import threading
from logging.handlers import RotatingFileHandler
import logging

load_dotenv()

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# создаем папку если его нет 
if not os.path.exists('logs'):
    try:
        os.mkdir('logs')
    except Exception as my_error:
        print(f"Ошибка: {my_error}") #debug
    
file_handler = RotatingFileHandler(
    'logs/taxi_calls.log', maxBytes=5242880,
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
    datefmt='%d-%m-%Y %H:%M:%S'
    )
)
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler) 
app.logger.setLevel(logging.INFO)

# устанавливаем стандартные параметры логирования
logging.basicConfig(
    filename='logs/myapi.log', 
    level=logging.INFO, 
    format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
    datefmt='%d-%m-%Y %H:%M:%S'
)
#загружаем переменные из .env
tokken = os.getenv('tokken')
app_debug = os.getenv('debug_on')
users_id = os.getenv('users_id')
my_host = os.getenv('my_host')
my_port = os.getenv('my_port')
bot_tokken = os.getenv('bot_tokken')
admins_id = os.getenv('admins_id')

@app.route('/favicon.ico')
def favicon():
    #print (app.root_path) #debug
    return send_from_directory(os.path.join(app.root_path, 'static'),
                            'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/api/test')
def index():
    return make_response(jsonify(
                    ok=True
                ), 200)

#GET мы не обрабатываем 
@app.route('/api/call/<tokken>', methods=['POST']) #уведомления в чат что появился новый клиент 
def connect(tokken):
    request_data = request.get_json()
    number = None
    
    if app_debug == "1":
        #print (json.dumps(request_data, indent=2, ensure_ascii = False)) #debug
        logging.info(f"[API]\nrequest_data: {json.dumps(request_data, indent=2, ensure_ascii = False)}")

    if request_data:
        #print (request_data) #debug
        if 'number' in request_data:
            number = request_data['number']
    
    #подготовка сообщения 
    if tokken == tokken:
        my_text = (
            f"Новый звонок\n<b>📱 +{number}</b>"   
        )
        bot_tokken = os.getenv('bot_tokken') #загружаем токкен бота из файла
        Bot = telebot.TeleBot(bot_tokken) #назначаем токкен в телебот

        try:
            Bot.send_message(users_id, my_text, parse_mode="HTML")
            if app_debug == "1":
                answer = { 'ok':True, 'tokken': 'tokken accepted', 'TelegramBot':'ok'}
                logging.info(f'[API]\nanswer: \n{json.dumps(answer, indent=2, ensure_ascii = False)}')
            return make_response(jsonify(
                ok=True,
                tokken="tokken accepted",
                TelegramBot="ok"
            ), 200)
        except Exception as my_error:
            print(f"Ошибка: {my_error}") #debug 
            if app_debug == "1":
                answer = { 'ok':False, 'tokken': 'tokken accepted', 'TelegramBot':'Forbidden: bot was blocked by the user'}
                logging.info(f'[API]\nanswer: \n{json.dumps(answer, indent=2, ensure_ascii = False)}')
            return make_response(jsonify(
            ok=False,
            tokken="tokken accepted",
            TelegramBot="Forbidden: bot was blocked by the user"
            ), 200)
    

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# -----------------------------------------------------------------
Bot = telebot.TeleBot(bot_tokken) #назначаем токкен в телебот
Bot.delete_my_commands(scope=None, language_code=None)
Bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "🏠 Главное меню"),
        telebot.types.BotCommand("id", "👤 Телеграм ID"),
        # telebot.types.BotCommand("test", "проверка работы бота")
    ],
    # scope=telebot.types.BotCommandScopeChat(12345678)  #use for personal command for users
    # scope=telebot.types.BotCommandScopeAllPrivateChats()  #use for all private chats
)
# -----------------------------------------------------------------

#обработка команды start
@Bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обрабатываем текстовые сообщения '/start' """
    user_id = message.from_user.id
    allow_user = users_id
    print (allow_user) #debug

@Bot.message_handler(commands=['id'])
def send_id(message):
    """ Обрабатываем текстовые сообщения '/id'. """
    if message.chat.type != 'private':
        Bot.send_message(message.chat.id, f"ID чата: {message.chat.id}")
    else:
        Bot.send_message(message.from_user.id, f"Ваш ID: {message.from_user.id}")

def flask_thread():
    #запускаем BotAPI
    app.logger.info('[API] startup')
    app.run(host=my_host, port=my_port, debug=False) 

def bot_thread():
    try:
        app.logger.info('[BOT] startup')
        #отправляем уведомеление в чат админу
        Bot.send_message(2964812, "Taxi Calls API на сервере bot02.wilgood.ru запустился") 
        #Непрекращающаяся прослушка наших чатов
        Bot.polling(none_stop=True, interval=0,  timeout=120) 
    except Exception as my_bot_error:
        app.logger.info(f'[BOT] startup, Ошибка: {my_bot_error}')
        app.logger.info(f'[BOT] Bot упал отжался и встал')
        # отправляем сообщение админу
        Bot.send_message(admins_id, f"Ошибка: {my_bot_error}")
        Bot.send_message(admins_id, "Bot упал отжался и встал") # отправляем сообщение админу
        #sleep(20)

# Запуск бота
if __name__ == '__main__':
    flask_app = threading.Thread(target=flask_thread)
    bot_app = threading.Thread(target=bot_thread)

    flask_app.start()
    bot_app.start()

    flask_app.join()
    bot_app.join()