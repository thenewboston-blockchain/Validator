import os

from celery import Celery

from config.helpers.environment import SETTINGS_MODULE

os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

app = Celery('tasks')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.update(
    task_routes={
        'v1.tasks.block_queue.process_block_queue': {'queue': 'block_queue'},
    },
)

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
