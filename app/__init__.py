from flask import Flask
from celery import Celery

from app.api import blueprint as api_blueprint
from app.extensions import db

CELERY_TASK_LIST = [
    'app.tasks'
]


def create_celery_app(app=None):
    """
    Creation de l'application Celery avec le context de l'application Flask

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app()

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'],
                    include=CELERY_TASK_LIST)
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_app():
    """
    Creation de l'application Flask
    :return: 
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config')

    app.register_blueprint(api_blueprint, url_prefix='/api')

    extensions(app)

    with app.app_context():
        from app.models import FlightPlan, Waypoint, DroneParameters, Gimbal, GPSCoord, FlightPlanBuilder
        #db.drop_all()
        db.create_all()

    return app


def extensions(app):
    """
    Initialisation des extensions

    :param app: Flask app
    :return: None
    """
    db.init_app(app)
