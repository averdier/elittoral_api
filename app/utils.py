from datetime import datetime
from config import ALLOWED_EXTENSIONS


def is_float(data):
    """
    Indique si une donnee peut etre un float

    :param data: Donne a tester
    :type data: object
    :return: True si la donnee peut etre un float, False sinon
    :rtype: bool
    """
    try:
        float(data)
        return True
    except ValueError:
        return False


def is_int(data):
    """
    Indique si une donnee peut etre un int

    :param data: Donnee a tester
    :type data: object
    :return: True si la donnee peut etre un int, False sinon
    :rtype: bool
    """
    try:
        int(data)
        return True
    except ValueError:
        return False


def is_string(data):
    """
    Indique si une donnee peut etre un string

    :param data: Donnee a tester
    :type data: object
    :return: True si la donnee peut etre un string, False sinon
    :rtype: bool
    """
    try:
        str(data)
        return True
    except ValueError:
        return False


def is_valid_date(date, date_format):
    """
    Indique si une chaine de caracteres peut etre une date

    :param date: Date sous forme de chaine de caracteres
    :param date_format: Format de la date
    :type date: string
    :type date_format: string

    :return: True si la chaine peut etre une date, False sinon
    :rtype: bool
    """
    try:
        datetime.strptime(date, date_format)
        return True
    except ValueError as e:
        return False


def get_name_without_extentsion(filename):
    """
    Retourne le nom de fichier sans l'extension

    :param filename: Nom du fichier
    :type filename: str
    :return: Nom du fichier sans l'extension
    :rtype: str
    """
    name = ''
    if '.' in filename:
        name = filename.rsplit('.', 1)[0].lower()
    return name


def get_extention(filename):
    """
    Retourne l'extension d'un nom de fichier

    :param filename: Nom du fichier
    :type filename: string

    :return: Extension du fichier
    :rtype: string
    """
    extension = ''
    if '.' in filename:
        extension = filename.rsplit('.', 1)[1].lower()
    return extension


def allowed_file(filename):
    """
    Indique si un fichier est valide pour le serveur

    :param filename: Nom du fichier avec extension
    :type filename: string

    :return: True si le fichier est valide
    :rtype: bool
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

