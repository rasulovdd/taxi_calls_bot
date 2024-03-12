""" Модуль для работы с db """
import json
import os
from mysql.connector import MySQLConnection, Error  # Добавляем функцию MySQLConnection
from dotenv import load_dotenv
from time import time
from src import app01
#import logging

# устанавливаем стандартные параметры логирования
# logging.basicConfig(
#     filename='logs/taxi_calls.log', 
#     level=logging.INFO, 
#     format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s',
#     datefmt='%d-%m-%Y %H:%M:%S'
# )

load_dotenv()

mobapp_user=os.getenv('mobapp_user')
mobapp_pass=os.getenv('mobapp_pass')
hostname = os.getenv('hostname')

def read_db_config():
    db = {}
    db["host"] =os.getenv('db_host')
    db["user"] =os.getenv('db_user')
    db["password"]=os.getenv('db_password')
    db["database"]=os.getenv('database')
    db["port"]="3306"
    
    return db

db_config = read_db_config()  # получаем настройки для подключения к БД

# Записываем пользователя
def set_user_id(user_id, full_name, admin):
    """ записываем user_id в базу """
    #print ("set_user_id") #debug
    try:
        conn = MySQLConnection(**db_config)  # открывем соединение
        cursor = conn.cursor()  # открывем соединение
        cursor.execute(
            "INSERT INTO managers (user_id, full_name, admin) VALUES (%s,%s,%s)", 
            (user_id, full_name, admin)
        )
        conn.commit()  # Подтверждаем изменения
        cursor.close()  # Закрываем курсор
        conn.close()  # Закрываем соединение
        app01.logger.info(f"[DB] Новый пользователь: {user_id}. Добавлен")
    except Error as error:
        #print(error)
        app01.logger.error(f"[DB] Новый пользователь: {user_id}. Ошибка: {error}")
    

def is_user_exists(user_id):
    """ сушествует ли пользователь """
    status=''
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        query = (f"SELECT * FROM managers WHERE user_id='{user_id}'")
        cursor.execute(query)
        row = cursor.fetchone()
        if row:
            status = row[0]
        else:
            status = None
        cursor.close()
        conn.close()  # Закрываем соединение
        app01.logger.info(f"[DB] [is_user_exists] UserID: {user_id}. Информация получено")
    except Error as error:
        app01.logger.error(f"[DB] UserID: {user_id}. Ошибка [{error}]")
    return status

#получаем id всех пользователей    
def get_all_users(status):
    """ получаем id всех пользователей """
    all_users=[]
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(f"SELECT user_id FROM managers WHERE admin='{status}'")
        rows = cursor.fetchall()
        if rows:
            #all_users = rows
            for row in rows:
                all_users.append(row[0])
        else:
            all_users=None
        cursor.close()
        conn.close()
        app01.logger.info(f"[DB] [get_all_users] Информация получено")
    except Exception as e:
        print(e)
        app01.logger.error(f"[DB] [get_all_users] Ошибка [{e}]")
    return all_users

# Записываем контакт клиента 
def set_number(number):
    """ Записываем контакт клиента"""
    #print ("set_user_id") #debug
    try:
        conn = MySQLConnection(**db_config)  # открывем соединение
        cursor = conn.cursor()  # открывем соединение
        cursor.execute("INSERT INTO client (number) VALUES (%s)", (number,))
        conn.commit()  # Подтверждаем изменения
        cursor.close()  # Закрываем курсор
        app01.logger.info(f"[DB] [set_number] успешно")
        conn.close()  # Закрываем соединение
    except Error as error:
        print(error)
        app01.logger.error(f"[DB] [set_number] Ошибка: {error}")
    
# даем права admin
def set_admin(user_id, status):
    """даем права admin"""
    try:
        conn = MySQLConnection(**db_config)  # открывем соединение
        #conn = mysql.connector.connect(**db_config)  # открывем соединение
        cursor = conn.cursor()  # открывем соединение
        cursor.execute(f"UPDATE managers SET admin='{status}' WHERE user_id='{user_id}'")
        conn.commit()  # Подтверждаем изменения
        cursor.close()  # Закрываем курсор
        conn.close()  # Закрываем соединение
        app01.logger.info(f"[DB] [set_admin] права админа выданы. UserID: {user_id}")
    except Error as error:
        print("set_admin:", error)
        app01.logger.error(f"[DB] [set_admin] Ошибка: {error}")
    