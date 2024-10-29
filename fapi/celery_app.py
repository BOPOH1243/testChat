from celery import Celery
from tasks import delete_old_tokens
app = Celery('tasks', broker='redis://localhost:6379/0')


app.conf.beat_schedule = {
    'delete-every-5-minutes': {
        'task': 'tasks.delete_old_tokens',
        'schedule': 300.0,  # 5 минут в секундах
    },
}
