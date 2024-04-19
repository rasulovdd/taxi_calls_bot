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
from time import sleep
import threading
from logging.handlers import RotatingFileHandler
import logging
from src import db
from src import app01

load_dotenv()

# app01 = Flask(__name__)
# app01.config['JSON_SORT_KEYS'] = False

# создаем папку если его нет 
if not os.path.exists('logs'):
    try:
        os.mkdir('logs')
    except Exception as my_error:
        print(f"Ошибка: {my_error}") #debug
    
# file_handler = RotatingFileHandler(
#     'logs/taxi_calls.log', maxBytes=5242880,
#     backupCount=10
# )
# file_handler.setFormatter(logging.Formatter(
#     '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
#     datefmt='%d-%m-%Y %H:%M:%S'
#     )
# )
# file_handler.setLevel(logging.INFO)
# app01.logger.addHandler(file_handler) 
# app01.logger.setLevel(logging.INFO)

# # устанавливаем стандартные параметры логирования
# logging.basicConfig(
#     filename='logs/myapi.log', 
#     level=logging.INFO, 
#     format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
#     datefmt='%d-%m-%Y %H:%M:%S'
# )

#загружаем переменные из .env
api_tokken = os.getenv('api_tokken')
app_debug = os.getenv('debug_on')
#users_id_all = os.getenv('users_id')
#users_id = users_id_all.split(",")
my_host = os.getenv('my_host')
my_port = os.getenv('my_port')
bot_tokken = os.getenv('bot_tokken')
admins_id = os.getenv('admins_id')

bot_tokken = os.getenv('bot_tokken') #загружаем токкен бота из файла
Bot = telebot.TeleBot(bot_tokken) #назначаем токкен в телебот

@app01.route('/favicon.ico')
def favicon():
    #print (app.root_path) #debug
    return send_from_directory(os.path.join(app01.root_path, 'static'),
                            'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app01.route('/api/test')
def index():
    return make_response(jsonify(
                    ok=True
                ), 200)

#GET мы не обрабатываем 
@app01.route('/api/call/<tokken>', methods=['POST']) #уведомления в чат что появился новый клиент 
def connect(tokken):
    request_data = request.get_json()
    number = None
    status = None
    
    if app_debug == "1":
        #print (json.dumps(request_data, indent=2, ensure_ascii = False)) #debug
        app01.logger.info(f"[API]\nrequest_data: {json.dumps(request_data, indent=2, ensure_ascii = False)}")

    if request_data:
        #print (request_data) #debug
        if 'number' in request_data:
            number = request_data['number']
        if 'status' in request_data:
            if request_data['status'] == "1":
                status = "✅"
            else:
                status = "❌"

    #подготовка сообщения 
    if tokken == api_tokken:
        #возврашаем что все ок
        if app_debug == "1":
            answer = { 'ok':True, 'tokken': 'tokken accepted'}
            app01.logger.info(f'[API]\nanswer: \n{json.dumps(answer, indent=2, ensure_ascii = False)}')
        #уведомляем пользователей
        notifications(number, status) 
        #возврашаем результат
        return make_response(jsonify(
                                ok=True,
                                tokken="tokken accepted"
                            ), 200) 
    else:
        if app_debug == "1":
            answer = { 'ok':False, 'tokken': 'the token is not correct'}
            app01.logger.info(f'[API]\ntokken: {tokken}\nanswer: \n{json.dumps(answer, indent=2, ensure_ascii = False)}')
        return make_response(jsonify(
                            ok=False,
                            tokken="the token is not correct"
                            ), 404)        
    

def notifications(number, status):
    """Уведомляем пользователей"""
    #записываем номер клиента в базу
    db.set_number(number)
    my_text = (
            f"{status} Новый звонок\n<b>📱 {number}\n</b>"
        )
    all_users = db.get_all_users(1)
    #print (my_text) #debug
    for id in all_users:
        #print (id) #debug
        try:
            Bot.send_message(id, my_text, parse_mode="HTML")
            if app_debug == "1":
                app01.logger.info(f'[BOT] [UserID: {id}] Cообщение отправлено')
        except Exception as my_error:
            print(f"Ошибка: {my_error}") #debug 
            if app_debug == "1":
                app01.logger.error(f'[BOT] Ошибка: {my_error}')

@app01.errorhandler(404)
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
    full_name = message.from_user.full_name
    
    #если пользователь сушествует 
    if db.is_user_exists(user_id):
        #получаем список менеджеров (статус = 1)
        all_users = db.get_all_users(1)
        Bot.send_message(user_id, "Привет 🤝\nРад видеть вас снова")
        if int(user_id) in all_users:
            Bot.send_message(user_id, "✅ Теперь я буду уведомлять тебя о звонках на номер Taxi")
        else:
            Bot.send_message(user_id, "❌ У тебя нету доступа.\nОбратись пожалуйста к @RasulovDD")
            Bot.send_message(user_id, f"Твой ID: {user_id}")
    else:
        #записываем инфо в базу данных
        if int(user_id) == int(admins_id):
            #print ("admin") #debug
            db.set_user_id(user_id, full_name, 1)
        else:
            db.set_user_id(user_id, full_name, 0)
        
        #получаем список менеджеров (статус = 1)
        all_users = db.get_all_users(1)
        if int(user_id) in all_users:
            #print ("в списке пользователей")
            Bot.send_message(user_id, "Привет 🤝\n✅ Теперь я буду уведомлять тебя о звонках на номер Taxi")
        else:
            Bot.send_message(user_id, "Привет 🤝\n❌ У тебя нету доступа.\nОбратись пожалуйста к @RasulovDD")
            Bot.send_message(user_id, f"Твой ID: {user_id}")
    
    if app_debug == "1":
        app01.logger.info(f'[BOT] [UserID: {user_id}] Сообщение отправлено')
    
    #db.set_user_id(user_id, full_name, 0)
    # for id in users_id:
    #     if str(user_id) == str(id):
    #         bot_text = "✅Теперь я буду уведомлять тебя о звонках на номер taxi"
    #         Bot.send_message(user_id, bot_text)
    #         if app_debug == "1":
    #             app.logger.info(f'[BOT] [user_id:{user_id}] Сообщение отправлено')


@Bot.message_handler(commands=['id'])
def send_id(message):
    """ Обрабатываем текстовые сообщения '/id'. """
    if message.chat.type != 'private':
        Bot.send_message(message.chat.id, f"ID чата: {message.chat.id}")
    else:
        Bot.send_message(message.from_user.id, f"Ваш ID: {message.from_user.id}")

@Bot.message_handler(commands=['admin'])
def command_admin(message):
    """ Обрабатываем текстовые сообщения '/admin'. """
    text = message.text
    user_id = message.from_user.id
    #print (admin_id) #debug
    if int(user_id) == int(admins_id):
        #даем права админа
        try:
            manager_id = text.split(" ")[1]
        except:
            Bot.send_message(user_id, f"❌ Такая команда не поддерживается!")
            return

        db.set_admin(manager_id, 1)
        Bot.send_message(user_id, f"✅ UserID: {manager_id} Права админа, выданы")
        Bot.send_message(manager_id, "✅ Доступ получен!\nТеперь я буду уведомлять тебя о звонках на номер taxi")
        if app_debug == "1":
            app01.logger.info(f'[BOT] [UserID: {user_id}] Добавил менеджера {manager_id}')
    else:
        Bot.send_message(user_id, "❌ У Вас нет прав администратора")
        if app_debug == "1":
            app01.logger.info(f'[BOT] [UserID: {user_id}] не имеет права админ')

def flask_thread():
    #запускаем BotAPI
    app01.logger.info('[API] startup')
    app01.run(host=my_host, port=my_port, debug=False) 

def bot_thread():
    try:
        app01.logger.info('[BOT] startup')
        #отправляем уведомеление в чат админу
        Bot.send_message(2964812, "Taxi Calls API на сервере bot02.wilgood.ru запустился") 
        #Непрекращающаяся прослушка наших чатов
        Bot.polling(none_stop=True, interval=0,  timeout=120) 
    except Exception as my_bot_error:
        app01.logger.info(f'[BOT] startup, Ошибка: {my_bot_error}')
        app01.logger.info(f'[BOT] Bot упал')
        # отправляем сообщение админу
        Bot.send_message(admins_id, "Bot упал") # отправляем сообщение админу

# Запуск APP
if __name__ == '__main__':
    flask_app = threading.Thread(target=flask_thread)
    flask_app.start()
    
    # try:
    #     bot_app = threading.Thread(target=bot_thread)
    #     bot_app.start()
    #     bot_app.join()
    # except Exception as e:
    #     sleep(10) #ждем 10 сек
    #     print ("Ждем 10 секунд ........")
    #     app01.logger.info(f'[BOT] startup, Ошибка: {e}')
    #     app01.logger.info(f'[BOT] Bot упал отжался и встал')
    #     bot_app = threading.Thread(target=bot_thread)
    #     bot_app.start()
    #     bot_app.join()
    while True:
        try:
            app01.logger.info('[BOT] startup')
            #отправляем уведомеление в чат админу
            Bot.send_message(2964812, "Taxi Calls API на сервере bot02.wilgood.ru запустился") 
            #Непрекращающаяся прослушка наших чатов
            Bot.polling(none_stop=True, interval=0,  timeout=60) 
        except Exception as my_bot_error:
            app01.logger.info(f'[BOT] startup, Ошибка: {my_bot_error}')
            Bot.send_message(admins_id, f"Ошибка: {my_bot_error}") # отправляем сообщение админу
            app01.logger.info(f'[BOT] startup, Ждем 10 секунд ........')
            sleep(10) #ждем 10 сек
            app01.logger.info(f'[BOT] упал отжался и встал')
            # отправляем сообщение админу
            Bot.send_message(admins_id, "Bot упал отжался и встал") # отправляем сообщение админу
    
    #flask_app.join()

    
