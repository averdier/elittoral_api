import os
import numpy as np
import cv2
from config import THUMBNAIL_FOLDER
from app.extensions import db
from app.models import Resource


def build_thumbnail(resource):
    """
    Cree la vignette de la resource
    
    :param resource: Ressource a traiter
    :type resource: Resource
    """

    if not isinstance(resource, Resource):
        raise ValueError('Parameter resource have to be a Resource')

    resource_path = resource.get_content_path()

    if not os.path.exists(resource_path) or not os.path.isfile(resource_path):
        raise ValueError('Resource have no content')

    resource_img = cv2.imread(resource_path)
    ratio = 200.0 / resource_img.shape[1]
    new_dim = (200, int(resource_img.shape[0] * ratio))

    resource_thumbnail = cv2.resize(resource_img, new_dim, cv2.INTER_AREA)

    path = os.path.join(THUMBNAIL_FOLDER, resource.filename)
    cv2.imwrite(path, resource_thumbnail)



