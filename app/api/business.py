from datetime import datetime
from app.utils import is_float, is_int
from app.exceptions import ValueExist
from app.models import GPSCoord, Gimbal, DroneParameters, Waypoint, FlightPlan


def build_line_with_increment(coord1, coord2, increment, start_number, rotation, gimbal):
    """
    Retourne une liste de waypoint representant une ligne 

    :param coord1: Coordonnee 1
    :type coord1: GPSCoord

    :param coord2: Coordonnee 2
    :type coord2: GPSCoord

    :param increment: Increment (m)
    :type increment: float

    :param start_number: Numero de depart pour la numerotation des waypoints
    :type start_number: int

    :param rotation: Rotation du drone
    :type rotation: int

    :param gimbal: Parametres du gimbal du drone
    :type gimbal: Gimbal

    :return: Liste des waypoints representant la ligne
    :rtype: list<Waypoint>
    """

    if coord1 is None or not isinstance(coord1, GPSCoord):
        raise ValueError('coord1 required')

    if coord2 is None or not isinstance(coord2, GPSCoord):
        raise ValueError('coord2 required')

    if increment is None or not is_float(increment):
        raise ValueError('increment required')

    if rotation is None or not is_int(rotation):
        raise ValueError('rotation required')

    if start_number is None or not is_int(start_number):
        raise ValueError('start_number required')

    if gimbal is None or not isinstance(gimbal, Gimbal):
        raise ValueError('gimbal required')

    current_number = start_number

    result = [Waypoint(number=current_number,
                       parameters=DroneParameters(coord=coord1.clone(),
                                                  rotation=rotation,
                                                  gimbal=gimbal.clone()))]
    current_number += 1
    distance = coord1.pythagore_distance_to(coord2)
    nb_it = int(distance / increment)

    for i in range(1, nb_it):
        if current_number > 97:
            break

        last_waypoint = result[len(result) - 1]

        coord = last_waypoint.parameters.coord
        distance = coord.pythagore_distance_to(coord2)
        coef_direct = increment / distance

        dx = coord.lon + coef_direct * (coord2.lon - coord.lon)
        dy = coord.lat + coef_direct * (coord2.lat - coord.lat)
        dz = coord.alt + coef_direct * (coord2.alt - coord.alt)

        new_coord = GPSCoord(lat=dy, lon=dx, alt=dz)

        result.append(Waypoint(number=current_number,
                               parameters=DroneParameters(coord=new_coord,
                                                          rotation=rotation,
                                                          gimbal=gimbal.clone())))
        current_number += 1

    result.append(Waypoint(number=current_number,
                           parameters=DroneParameters(coord=coord2.clone(),
                                                      rotation=rotation,
                                                      gimbal=gimbal.clone())))
    return result


# <!> A revoir pour decoupage en fonctions
def build_vertical_flightplan(parameters):
    """
    Retourne un plan de vol vertical a partir des parametres

    :param parameters: Parametres pour la creation du plan de vol
    :type parameters: dict
        {
            'flightplan_name' : value, (required|string|unique|min_size[3]|max_size[64])
            'coord1'          :        (required)
                {
                    'lat' : value, (required|float|min[-90]|max[90])
                    'lon' : value (required|float|min[-180]|max[180])
                },
            'coord2'          :        (required)
                {
                    'lat' : value, (required|float|min[-90]|max[90])
                    'lon' : value (required|float|min[-180]|max[180])
                },
            'alt_start'      : value, (roptional|float|min[>0|default[1])
            'alt_end'        : value, (required|float|min[>alt_start])
            'h_increment'    : value, (required|float|min[>0)
            'v_increment'    : value, (required|float|min[>0)
            'r_otation'      : value, (optional|int|min[-180]|max[180]|default[0])
            'd_gimbal'       :        (optional, else need minimum 1 value)
                {
                    'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                    'pitch' : value, (optionnal|float|min[-180]|max[180]|default[90])
                    'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
                }
        }

    :return: Dictionnaire representant un plan de vol
    :rtype: dict
        {
            'name'      : string value
            'waypoints' : list<Waypoint>
        }
    """
    flightplan_name = parameters.get('flightplan_name')
    if FlightPlan.query.filter_by(name=flightplan_name).first() is not None:
        raise ValueExist('FlightPlan name already exist')

    coord1 = GPSCoord.from_dict(parameters.get('coord1'))
    coord2 = GPSCoord.from_dict(parameters.get('coord2'))

    alt_start = 1
    if parameters.get('alt_start') is not None:
        alt_start = float(parameters.get('alt_start'))
        if alt_start <= 0:
            raise ValueError('alt_start have to be upper 0')

    alt_end = float(parameters.get('alt_end'))
    if alt_end < alt_start:
        raise ValueError('alt_end have to be greater or equal to alt_start')

    h_increment = float(parameters.get('h_increment')) / 1000
    if h_increment <= 0:
        raise ValueError('h_increment have to be upper 0')

    v_increment = float(parameters.get('v_increment'))
    if v_increment <= 0:
        raise ValueError('v_increment have to be upper 0')

    d_rotation = 0
    if parameters.get('d_rotation') is not None:
        d_rotation = float(parameters.get('d_rotation'))

    d_gimbal = None
    if parameters.get('gimbal') is not None:
        d_gimbal = Gimbal.from_dict(parameters.get('gimbal'))
    else:
        d_gimbal = Gimbal()

    way_result = []
    current_number = 0
    alt_current = alt_start

    coord1.alt = alt_current
    coord2.alt = alt_current
    line = build_line_with_increment(coord1, coord2, h_increment, current_number, d_rotation, d_gimbal)
    way_result.append(line)

    current_number = len(line)
    alt_current += v_increment
    reverse = True

    while current_number < 99 and alt_current <= alt_end:
        last_line = way_result[len(way_result) - 1]
        new_line = []

        pos = []
        if reverse:
            reverse = False
            i = len(last_line) - 1
            while i >= 0:
                pos.append(i)
                i -= 1
        else:
            reverse = True
            for i in range(0, len(last_line)):
                pos.append(i)

        for i in range(0, len(pos)):
            if current_number > 98:
                break
            prev_waypoint = last_line[pos[i]]
            new_coord = GPSCoord(lat=prev_waypoint.parameters.coord.lat,
                                 lon=prev_waypoint.parameters.coord.lon,
                                 alt=alt_current)

            new_waypoint = Waypoint(number=current_number,
                                    parameters=DroneParameters(coord=new_coord,
                                                               rotation=prev_waypoint.parameters.rotation,
                                                               gimbal=prev_waypoint.parameters.gimbal.clone()))
            new_line.append(new_waypoint)
            current_number += 1

        way_result.append(new_line)
        alt_current += v_increment

    waypoint_list = []
    for i in range(0, len(way_result)):
        for j in range(0, len(way_result[i])):
            waypoint_list.append(way_result[i][j])
    return {
        'name': flightplan_name,
        'waypoints': waypoint_list
    }
