import os
import numpy as np
import cv2
from config import THUMBNAIL_FOLDER, RESULT_FOLDER
from app.utils import get_name_without_extentsion
from app.extensions import db
from app.models import ReconResource


def open_resource_content(resource):
    """
    Open resource content with opencv
    
    :param resource: Resource
    :type: ReconResource
    :return: cv2.imread
    """
    if not isinstance(resource, ReconResource):
        raise ValueError('Parameter resource have to be a Resource')

    resource_path = resource.get_content_path()

    if not os.path.exists(resource_path) or not os.path.isfile(resource_path):
        raise ValueError('Resource have no content')

    return cv2.imread(resource_path)


def save_result(minuend, subthrahend, result_img):
    """
    Save the analysis result
    
    :param minuend: Minuend ReconResource
    :param subthrahend: Subthrahend ReconResource
    :param result_img: cv2 result image
    :return: filename of result
    """

    filename = (get_name_without_extentsion(minuend.filename) + '_SUB_' + get_name_without_extentsion(
        subthrahend.filename)).upper() + '.jpg'
    path = os.path.join(RESULT_FOLDER, filename)
    cv2.imwrite(path, result_img)

    return filename


def build_thumbnail(resource):
    """
    Cree la vignette de la resource
    
    :param resource: Ressource a traiter
    :type resource: ReconResource
    """

    if not isinstance(resource, ReconResource):
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
