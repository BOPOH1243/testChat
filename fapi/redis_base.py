import redis

# Подключаемся к Redis (localhost и порт 6379 - значения по умолчанию)
redis_connect = redis.Redis(host='redis', port=6379, db=0)