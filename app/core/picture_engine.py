import os
import numpy as np
import cv2
from config import THUMBNAIL_FOLDER, RESULT_FOLDER
from app.utils import get_name_without_extentsion
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


def resource_subtraction(diminuend, subtrahend):
    """
    Subtract two resources
    
    :param diminuend: Diminuend resource
    :type diminuend: Resource
    
    :param subtrahend: Subtrahend resource
    :type subtrahend: Resource
    
    :return: Result filename
    :rtype: str
    """
    if not isinstance(diminuend, Resource):
        raise Exception('Parameter diminuend have to be a Resource')
    if not isinstance(subtrahend, Resource):
        raise Exception('Parameter subtrahend have to be a Resource')

    if diminuend.filename is None:
        raise Exception('Diminuend resource have no content file')
    if subtrahend.filename is None:
        raise Exception('Subtrahend resource have no content file')

    if not os.path.exists(diminuend.get_content_path()) and not os.path.isfile(diminuend.get_content_path()):
        raise Exception('Diminuend resource have no content file')
    if not os.path.exists(subtrahend.get_content_path()) and not os.path.isfile(subtrahend.get_content_path()):
        raise Exception('Subtrahend resource have no content file')

    diminuend_img = cv2.imread(diminuend.get_content_path())
    subtrahend_img = cv2.imread(subtrahend.get_content_path())

    substractor = cv2.createBackgroundSubtractorMOG2()
    mask = substractor.apply(diminuend_img)
    mask = substractor.apply(subtrahend_img)

    filename = get_name_without_extentsion(diminuend.filename) + '_SUB_' + get_name_without_extentsion(
        subtrahend.filename) + '.jpg'
    path = os.path.join(RESULT_FOLDER, filename)
    cv2.imwrite(path, mask)

    return filename


