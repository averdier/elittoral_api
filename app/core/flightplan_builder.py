from app.models import GPSCoord

def build_line_with_increment(coord1, coord2, increment):
    """
    Build horizontal line with increment from 2 gps coordinates
    
    :param coord1: Start coordinate
    :type coord1: GPSCoord
    
    :param coord2: End coordinate
    :type coord2: GPSCoord
    
    :param increment: Increment (m)
    :type increment: float
    
    :return: List of cordinates that represent the line
    :rtype: list[GPSCoord]
    """

    if not isinstance(coord1, GPSCoord):
        raise ValueError('Parameter coord1 have to be a GPSCoord')