web: gunicorn config.wsgi --log-file -
worker: celery worker --A config -l info -c 8