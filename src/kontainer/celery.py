from celery import Celery

from kontainer.app import app

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
