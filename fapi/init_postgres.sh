#!/bin/bash

# Установите переменные окружения для имени пользователя, базы данных и пароля
POSTGRES_USER=${POSTGRES_USER:-"username"}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-"password"}
POSTGRES_DB=${POSTGRES_DB:-"dbname"}

# Установка PostgreSQL
apt update && apt install -y postgresql postgresql-contrib

# Запуск PostgreSQL
service postgresql start

# Настройка PostgreSQL (создание пользователя и базы данных)
sudo -u postgres psql <<EOF
CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';
CREATE DATABASE $POSTGRES_DB;
GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
ALTER ROLE $POSTGRES_USER SET client_encoding TO 'utf8';
ALTER ROLE $POSTGRES_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $POSTGRES_USER SET timezone TO 'UTC';
EOF

# Настройка PostgreSQL для работы внутри Docker (разрешение внешнего подключения)
echo "listen_addresses='*'" >> /etc/postgresql/$(ls /etc/postgresql)/main/postgresql.conf
echo "host all all 0.0.0.0/0 md5" >> /etc/postgresql/$(ls /etc/postgresql)/main/pg_hba.conf

# Перезапуск PostgreSQL, чтобы применить изменения
service postgresql restart

echo "PostgreSQL установлен и запущен. База данных '$POSTGRES_DB' и пользователь '$POSTGRES_USER' созданы."
