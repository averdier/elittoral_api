import os
basedir = os.path.abspath(os.path.dirname(__file__))

# App settings
MAX_WAYPOINT = 99

# Redis settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# RESTPLUS settins
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# Content settings
UPLOAD_FOLDER = os.path.join(basedir, 'upload')
RESULT_FOLDER = os.path.join(basedir, 'result')
THUMBNAIL_FOLDER = os.path.join(basedir, 'thumbnail')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}