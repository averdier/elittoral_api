from config import MAX_WAYPOINT
from app.models import GPSCoord, Gimbal, Waypoint, DroneParameters, FlightPlanBuilder


def build_line_with_increment(coord1, coord2, increment, max_point, altitude=0):
    """
    Build horizontal line with increment from 2 gps coordinates
    
    :param coord1: Start coordinate
    :type coord1: GPSCoord
    
    :param coord2: End coordinate
    :type coord2: GPSCoord
    
    :param increment: Increment (m)
    :type increment: float
    
    :param max_point: Maximum number of coordinate in the path
    :type max_point: int
    
    :param altitude: Altitude (m)
    :type altitude: float
    
    :return: List of cordinates that represent the line
    :rtype: list[GPSCoord]
    """

    if not isinstance(coord1, GPSCoord):
        raise ValueError('Parameter coord1 have to be a GPSCoord')

    if not isinstance(coord2, GPSCoord):
        raise ValueError('Parameter coord2 have to be a GPSCoord')

    increment = float(increment)

    start_coord = coord1.clone()
    start_coord.alt = altitude
    result = [start_coord]

    distance = coord1.distance_to(coord2).meters

    nb_point = int(distance / increment)

    if nb_point > max_point:
        nb_point = max_point

    for i in range(1, nb_point):
        last_coord = result[len(result) - 1]
        distance = last_coord.distance_to(coord2).meters
        coef_direct = increment / distance

        dx = last_coord.lon + coef_direct * (coord2.lon - last_coord.lon)
        dy = last_coord.lat + coef_direct * (coord2.lat - last_coord.lat)

        new_coord = GPSCoord(lat=dy, lon=dx, alt=altitude)

        result.append(new_coord)

    end_coord = coord2.clone()
    end_coord.alt = altitude
    result.append(end_coord)

    return result


def create_waypoints_from_path(path, max_number, rotation, gimbal):
    """
    Create Waypoints list from path of GPSCoord

    :param path: Path of GPSCoord
    :type path: list[GPSCoord]

    :param rotation: Drone rotation
    :type rotation: float

    :param gimbal: Gimbal for waypoints
    :type gimbal: Gimbal

    :param max_number: Max number for Waypoints
    :type max_number: int

    :return: List of Waypoints
    :rtype: list[Waypoint]
    """
    if path is None:
        raise ValueError('Parameter line required')

    if not isinstance(gimbal, Gimbal):
        raise ValueError('Parameter gimbal have to be a Gimbal')

    rotation = float(rotation)
    max_number = int(max_number)

    result = []

    for i in range(0, len(path)):
        if i >= max_number:
            break

        new_coord = GPSCoord(
            lat=path[i].lat,
            lon=path[i].lon,
            alt=path[i].alt
        )

        new_parameters = DroneParameters(
            rotation=rotation,
            gimbal=gimbal.clone(),
            coord=new_coord
        )

        new_waypoint = Waypoint(
            number=i,
            parameters=new_parameters
        )

        result.append(new_waypoint)

    return result


def build_vertical_path_with_increments(coord1, coord2, horizontal_increment, vertical_increment, start_alt, end_alt,
                                        max_point):
    """
    Build a vertical path 
    
    :param coord1: Start coordinate
    :type coord1: GPSCoord
    
    :param coord2: End coordinate
    :type coord2: GPSCoord
    
    :param horizontal_increment: Horizontal increment (m)
    :type horizontal_increment: float
    
    :param vertical_increment:  Vertical increment (m)
    :type vertical_increment: float
    
    :param start_alt: Start altitude 
    :type start_alt: float
    
    :param end_alt: End altitutde
    :type end_alt: float
    
    :param max_point: Maximum number of coordinate in the path
    :type max_point: int
    
    :return: List of cordinates that represent the path
    :rtype: list[GPSCoord]
    """

    if not isinstance(coord1, GPSCoord):
        raise ValueError('Parameter coord1 have to be a GPSCoord')

    if not isinstance(coord2, GPSCoord):
        raise ValueError('Parameter coord2 have to be a GPSCoord')

    if coord1 == coord2:
        raise ValueError('The coordinates have the same position')

    horizontal_increment = float(horizontal_increment)
    vertical_increment = float(vertical_increment)
    start_alt = float(start_alt)
    end_alt = float(end_alt)
    max_point = int(max_point)

    base_line = build_line_with_increment(coord1, coord2, horizontal_increment, max_point, start_alt)

    result = []
    result.extend(base_line)

    current_alt = start_alt + vertical_increment
    do_reverse = True

    while len(result) < max_point and current_alt <= end_alt:
        if do_reverse:
            new_line = build_line_with_increment(coord2, coord1, horizontal_increment, max_point - len(result),
                                                 current_alt)

        else:
            new_line = build_line_with_increment(coord1, coord2, horizontal_increment, max_point - len(result),
                                                 current_alt)

        do_reverse = not do_reverse
        result.extend(new_line)
        current_alt += vertical_increment

    return result


def build_vertical_flightplan(coord1, coord2, horizontal_increment, vertical_increment, start_alt, end_alt,
                              max_waypoint, rotation, gimbal):
    """
    Build a vertical flightplan from parameters
    
    :param coord1: Start coordinate
    :type coord1: GPSCoord
    
    :param coord2: End coordinate
    :type coord2: GPSCoord
    
    :param horizontal_increment: Horizontal increment (m)
    :type horizontal_increment: float
    
    :param vertical_increment: Vertical increment (m)
    :type vertical_increment: float
    
    :param start_alt: Start altitude
    :type start_alt: float
    
    :param end_alt: End altitude
    :type end_alt: float
    
    :param max_waypoint: Maximum number of waypoints
    :type max_waypoint: int
    
    :param rotation: Drone rotation (°)
    :type rotation: float
    
    :param gimbal: Gimbal parameters
    :type gimbal: Gimbal
    
    :return: List of waypoint that represent the flightplan
    :rtype: list[Waypoint]
    """

    # No special verification, functions used already handle errors

    coord_path = build_vertical_path_with_increments(coord1, coord2, horizontal_increment, vertical_increment,
                                                     start_alt, end_alt, max_waypoint)

    flightplan_path = create_waypoints_from_path(coord_path, max_waypoint, rotation, gimbal)

    return flightplan_path


def build_vertical_flightplan_from_options(builder_options):
    """
    Build a vertical flightplan from args (json request)
    
    :param builder_options: Builder options
    :type builder_options: FlightPlanBuilder
    
    :return: Path du plan de vol
    :rtype: list[Waypoint]
    """

    if not isinstance(builder_options, FlightPlanBuilder):
        raise ValueError('Parameter builder_options have to be a FlightPlanBuilder')

    return build_vertical_flightplan(
        builder_options.coord1,
        builder_options.coord2,
        builder_options.h_increment,
        builder_options.v_increment,
        builder_options.alt_start,
        builder_options.alt_end,
        MAX_WAYPOINT,
        builder_options.d_rotation,
        builder_options.d_gimbal
    )