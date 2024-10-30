#!/bin/bash

# Установка переменных окружения для имени пользователя, базы данных и пароля
POSTGRES_USER=${POSTGRES_USER:-"myuser"}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"mypassword"}
POSTGRES_DB=${POSTGRES_DB:-"mydb"}

# Установка PostgreSQL
apt update && apt install -y postgresql postgresql-contrib

# Запуск PostgreSQL
service postgresql start

# Настройка PostgreSQL (создание пользователя и базы данных)
sudo -u postgres psql <<EOF
DROP DATABASE IF EXISTS $POSTGRES_DB;
DROP USER IF EXISTS $POSTGRES_USER;

CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;

\c $POSTGRES_DB;

GRANT ALL PRIVILEGES ON SCHEMA public TO $POSTGRES_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $POSTGRES_USER;
EOF

# Настройка PostgreSQL для работы внутри Docker (разрешение внешнего подключения)
echo "listen_addresses='*'" >> /etc/postgresql/$(ls /etc/postgresql)/main/postgresql.conf
echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/$(ls /etc/postgresql)/main/pg_hba.conf

# Перезапуск PostgreSQL, чтобы применить изменения
service postgresql restart

echo "PostgreSQL установлен и запущен. База данных '$POSTGRES_DB' и пользователь '$POSTGRES_USER' созданы."
