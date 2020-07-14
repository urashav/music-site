import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'get_tracks_from_playlist_every_minute': {
        'task': 'music.tasks.get_tracks_from_api_playlist',
        'schedule': crontab(minute='*/1'),
    }
}