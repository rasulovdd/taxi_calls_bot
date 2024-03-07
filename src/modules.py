import imp
import requests, json
from mysql.connector import MySQLConnection, Error  # Добавляем функцию MySQLConnection
from dotenv import load_dotenv
import os

load_dotenv()

def read_db_config():
    db = {}
    db["host"] =os.getenv('host')
    db["user"] =os.getenv('user')
    db["password"]=os.getenv('password')
    db["database"]=os.getenv('database')
    
    return db

#отправляем сообщение
def send_message(bot_token, chat_id, my_text):
    session = requests.Session()
    PARAMS = {
                "chat_id" : chat_id,
                "text" : my_text,
    }
    
    #print (payload) #debug
    response = session.post(f"http://api.telegram.org/bot{bot_token}/sendmessage", params=PARAMS)
    #print (response.text) #debug
    
    my_data = json.loads(response.text)
    
    if my_data["ok"]:
        my_message = "ok"
    else:
        my_message = my_data["description"]

    #print (my_message) #debug
    return my_message

#устанавливаем статус пользователю 
def set_status(user_id, status):
    query = f"UPDATE main SET status='{status}' WHERE user_id='{user_id}'"  # Формируем запрос в базу данных
    # print (query)
    try:
        db_config = read_db_config()  # получаем настройки для подключения к БД
        conn = MySQLConnection(**db_config)  # открывем соединение
        cursor = conn.cursor()  # Открываем курсор
        cursor.execute(query)  # Выполняем запрос
        # print("выполняем set_status...")
        conn.commit()  # Подтверждаем изменения
        cursor.close()  # Закрываем курсор
        conn.close()  # Закрываем курсор
        #print (query) #debug
    except Error as error:
        print(error)

#получаем id всех пользователей    
def get_all_users():
    all_users=[]
    try:
        dbconfig = read_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM main")
        row = cursor.fetchone()
        if row is None:
            # print ("Not Found")
            all_users = [0]
        while row is not None:
            all_users.append(row[0])
            row = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
    return all_users