from app import create_celery_app
from app.core.picture_engine import build_thumbnail
from app.models import Resource


celery = create_celery_app()

@celery.task
def task_build_thumbnail(resource_id):
    """
    Tache de generation de la vignette
    
    :param resource_id: Resource unique Id
    :type resource_id: int
    """

    resource = Resource.query.filter_by(id = resource_id).first()

    if resource is None:
        raise ValueError('Resource #' + str(resource_id) + ' not found')

    build_thumbnail(resource)