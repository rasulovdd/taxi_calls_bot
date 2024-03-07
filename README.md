<h1 align="center">taxi_calls_bot</h1>

## Описание

Бот для работы со звонками такси

## Стек
Core: python 3, pyTelegramBotAPI, Flask-RESTful <br/>
Database: mysql<br/>

## Установка

1. Скачайте репозиторий<br/>

    ```bash
    git clone https://github.com/rasulovdd/taxi_calls_bot.git && cd taxi_calls_bot
    ```

2. Устанавливаем виртуальное окружение<br/>

    ```bash
    apt install -y python3-venv
    ```
    ```bash
    python3 -m venv env
    ```

3. Активируем её <br/>

    ```bash
    source env/bin/activate
    ```

4. Скачиваем и устанавливаем нужные библиотеки<br/>

    ```bash
    pip install -r requirements.txt
    ```

5. Изменить в скрипте mysql-setup.sh следующие параметры: <br/>
    
    Пользователь: bot_user
    Пароль: bot_password1!
    База данных: taxi_calls_bot

6. Запустить скрипт mysql-setup.sh<br/>
    даем права 
    ```bash
    chmod +x mysql-setup.sh
    ```
    запускаем скрипт
    ```bash
    /root/taxi_calls_bot/mysql-setup.sh
    ```

7. Создаем .env файл с вашими данными, можно создать из шаблона и просто поправить поля <br/>

    ```bash
    cp .env.sample .env
    nano .env
    ```

8. Создаем .service файл для вашего бота 
    sudo nano /etc/systemd/system/taxi_calls_bot.service<br/>

    ```ini
    [Unit]
    Description='Service for taxi_calls_bot'
    After=network.target

    [Service]
    Type=idle
    Restart=on-failure
    StartLimitBurst=2
    # Restart, but not more than once every 30s (for testing purposes)
    StartLimitInterval=120
    User=root
    ExecStart=/bin/bash -c 'cd ~/taxi_calls_bot/ && source env/bin/activate && python3 app.py'

    [Install]
    WantedBy=multi-user.target

    ```

9. Включаем сервис и запускаем<br/>

    ```bash
    systemctl enable taxi_calls_bot.service
    systemctl start taxi_calls_bot.service
    ```

10. Бот готов к использованию 

## Дополнительно

Чтобы бот мог присылать уведомления, необходимо в .env фале указать ID пользователя (пользователей) в users_id через запятую

пример заполнения .env файла:

    bot_tokken="Токен бота"
    tokken="токен доступа к BotAPI"
    db_host="127.0.0.1" #Адрес базы данных
    db_user="bot_user" #имя пользователя БД
    db_password="bot_password1!" #пароль пользователя БД
    database="taxi_calls_bot" #название БД
    my_host="10.10.1.111" #адрес сервера где будет работать BotAPI
    my_port="5010" #порт сервера где будет работать BotAPI
    users_id="2964812" #список пользователей для уведомления
    admins_id="2964812" #список пользователей c правами администратора
    debug_on=1 #статус debug режима


