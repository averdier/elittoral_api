from app.models import GPSCoord, Gimbal, Waypoint, DroneParameters


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

    if not isinstance(coord2, GPSCoord):
        raise ValueError('Parameter coord2 have to be a GPSCoord')
    increment = float(increment)

    result = [coord1.clone()]

    distance = coord1.distance_to(coord2).meters

    nb_it = int(distance / increment)

    for i in range(1, nb_it):
        last_coord = result[len(result) - 1]
        distance = last_coord.distance_to(coord2).meters
        coef_direct = increment / distance

        dx = last_coord.lon + coef_direct * (coord2.lon - last_coord.lon)
        dy = last_coord.lat + coef_direct * (coord2.lat - last_coord.lat)

        new_coord = GPSCoord(lat=dy, lon=dx)

        result.append(new_coord)

    return result


def build_waypoints_from_line(line, rotation, gimbal, altitude, start_number, max_number):
    """
    Build Waypoints list from line of GPSCoord
    
    :param line: Line of GPSCoord
    :type line: list[GPSCoord]
    
    :param rotation: Drone rotation
    :type rotation: float
    
    :param gimbal: Gimbal for waypoints
    :type gimbal: Gimbal
    
    :param altitude: Altitude of Waypoints (m)
    :type altitude: float
    
    :param start_number: Start number for Waypoints
    :type start_number: int
    
    :param max_number: Max number for Waypoints
    :type max_number: int
    
    :return: List of Waypoints
    :rtype: list[Waypoint]
    """

    if line is None:
        raise ValueError('Parameter line required')

    if not isinstance(gimbal, Gimbal):
        raise ValueError('Parameter drone_parameter have to be a DroneParameters')

    rotation = float(rotation)
    altitude = float(altitude)
    start_number = int(start_number)
    max_number = int(max_number)

    result = []
    current_number = start_number

    for i in range(0, len(line)):
        if current_number >= max_number:
            break

        new_coord = GPSCoord(
            lat = line[i].lat,
            lon = line[i].lon,
            alt = altitude
        )

        new_parameters = DroneParameters(
            rotation = rotation,
            gimbal = gimbal.clone(),
            coord = new_coord
        )

        new_waypoint = Waypoint(
            number = current_number,
            parameters = new_parameters
        )

        result.append(new_waypoint)
        current_number += 1

    return result
