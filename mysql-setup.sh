# Установка MySQL
sudo apt-get update
sudo apt-get install mysql-server -y

# Добавление MySQL в автозагрузку
sudo systemctl enable mysql

# Настройка базы данных
sudo mysql <<EOF
CREATE DATABASE taxi_calls_bot;
CREATE USER 'bot_user'@'localhost' IDENTIFIED BY 'bot_password1!';
GRANT ALL PRIVILEGES ON taxi_calls_bot.* TO 'bot_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Создание таблицы 'client' и 'managers' в базе данных 'taxi_calls_bot'
sudo mysql -e "USE taxi_calls_bot;
CREATE TABLE IF NOT EXISTS client (
  id int(10) PRIMARY KEY AUTO_INCREMENT,
  date TIMESTAMP NULL DEFAULT (now()),
  number TEXT NULL DEFAULT NULL
);
CREATE TABLE IF NOT EXISTS managers (
  id int(10) PRIMARY KEY AUTO_INCREMENT,
  date TIMESTAMP NULL DEFAULT (now()),
  user_id BIGINT UNIQUE INDEX,
  full_name VARCHAR NULL DEFAULT NULL,
  admin INT(10) NOT NULL DEFAULT '0',
);"

sudo sed -i 's/bind-address.*/bind-address = 127.0.0.1/' /etc/mysql/mysql.conf.d/mysqld.cnf

# Установка часового пояса в Moscow
sudo mysql -e "SET GLOBAL time_zone = '+3:00';"
sudo mysql -e "SET SESSION time_zone = '+3:00';"

# Перезапуск MySQL для применения изменений
sudo systemctl restart mysql

echo "MySQL установлен и настроен успешно."
echo "Пользователь: bot_user"
echo "Пароль: bot_password1!"
echo "База данных: taxi_calls_bot"
echo "Таблицы: users"