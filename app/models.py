import os
import math
from datetime import datetime
from config import UPLOAD_FOLDER, RESULT_FOLDER
from app.utils import is_float, is_int, is_string, is_valid_date, get_extention, allowed_file
from app.exceptions import ValueExist
from app.extensions import db

CONST_LON = 71.5
CONST_LAT = 111.3


class GPSCoord(db.Model):
    """
    Classe representant une coordonnee GPS
    """
    __tablename__ = 'gps_coord'
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.Float, index=True)
    lon = db.Column(db.Float, index=True)
    alt = db.Column(db.Float, index=True, default=1.0)

    @staticmethod
    def from_dict(args):
        """
        Retourne une coordonnee GPS a partir d'un dictionnaire

        :param args: Dictionnaire representant la coordonnee GPS
        :type  args: dict
            {
                'lat' : value, (required|float|min[-90]|max[90])
                'lon' : value, (required|float|min[-180]|max[180])
                'alt' : value  (optionnal|float|default[1])
            }
        :return: Coordonnee GPS
        :rtype: GPSCoord

        :raise ValueError: Si dict == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if args is None:
            raise ValueError('GPSCoord args required')

        coord = GPSCoord()
        coord.set_lat(args.get('lat'))
        coord.set_lon(args.get('lon'))

        if args.get('alt') is not None:
            coord.set_alt(args.get('alt'))

        return coord

    def update_from_dict(self, args):
        """
        Modifie la coordonnee GPS a partir d'un dictionnaire

        :param args: Dictionnaire representant les donnees a modifier
        :type args: dict
            {
                'lat' : value, (optionnal|float|min[-90]|max[90])
                'lon' : value, (optionnal|float|min[-180]|max[180])
                'alt' : value  (optionnal|float)
            }

        :raise ValueError: Si dict == None ou si il n'y as aucune donnees a mettre a jour, ou si erreur de validation
        :raise TypeError: Si erreur de validation du contenu
        """
        if args is None:
            raise ValueError('GPSCoord args required')

        lat = args.get('lat')
        lon = args.get('lon')
        alt = args.get('alt')

        if lat is None and lon is None and alt is None:
            raise ValueError('No data found in GPSCoord args')

        if lat is not None:
            self.set_lat(lat)

        if lon is not None:
            self.set_lon(lon)

        if alt is not None:
            self.set_alt(alt)

        db.session.add(self)

    def pythagore_distance_to(self, coord):
        """
        Calcule la distance entre 2 coordonnees

        :param coord: Coordonnee GPS
        :type coord: GPSCoord

        :return: Distance entre les deux coordonnees (en KM)
        :rtype: float
        """

        dx = CONST_LON * (self.lon - coord.lon)
        dy = CONST_LAT * (self.lat - coord.lat)
        dz = 0.0

        if self.alt != coord.alt:
            dz = (self.alt - coord.alt)

        return math.sqrt(math.pow(dx, 2) + math.pow(dy, 2) + math.pow(dz, 2))

    def set_lat(self, lat):
        """
        Modifie la latitude

        :param lat: Latitude
        :type  lat: float|string

        :raise ValueError: Si lat == None ou lat < -90 ou lat > 90
        :raise TypeError: Si lat n'est pas un float et qu'il ne peux pas etre converti en float
        """
        if lat is None:
            raise ValueError('GPSCoord lat is required')
        if not is_float(lat):
            raise TypeError('GPSCoord lat have to be a float')
        lat = float(lat)

        if lat < -90 or lat > 90:
            raise ValueError('GPSCoord lat have to be between -90 and 90')
        self.lat = lat

    def set_lon(self, lon):
        """
        Modifie la longitude

        :param lon: Longitude
        :type  lon: float|string

        :raise ValueError: Si lon == None ou lon < -180 ou lon > 180
        :raise TypeError: Si lon n'est pas un float et qu'il ne peux pas etre converti en float
        """
        if lon is None:
            raise ValueError('GPSCoord lon is required')
        if not is_float(lon):
            raise TypeError('GPSCoord lon have to be a float')
        lon = float(lon)

        if lon < -180 or lon > 180:
            raise ValueError('GPSCoord lon have to be between -180 and 180')
        self.lon = lon

    def set_alt(self, alt):
        """
        Modifie l'altitude

        :param alt: Altitude
        :type  alt: float|string

        :raise ValueError: Si alt == None
        :raise TypeError: Si alt n'est pas un float et qu'il ne peux pas etre converti en float
        """
        if alt is None:
            raise ValueError('GPSCoord alt is required')
        if not is_float(alt):
            raise TypeError('GPSCoord alt have to be a float')
        self.alt = float(alt)

    def clone(self):
        """
        Retourne une copie de la coordonnee

        :return: Copie de la coordonnee
        :rtype: GPSCoord
        """
        return GPSCoord(lat=self.lat, lon=self.lon, alt=self.alt)


class Gimbal(db.Model):
    """
    Classe representant les parametres d'un gimbal
    """
    __tablename__ = 'gimbal'
    id = db.Column(db.Integer, primary_key=True)
    yaw = db.Column(db.Float, index=True, default=0.0)
    pitch = db.Column(db.Float, index=True, default=0.0)
    roll = db.Column(db.Float, index=True, default=0.0)

    @staticmethod
    def from_dict(args):
        """
        Retourne un gimbal a partir d'un dictionnaire

        :param args: Dictionnaire representant les parametres du gimbal
        :type args: dict
            {
                'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                'pitch' : value, (optionnal|float|min[-180]|max[180]|default[0])
                'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
            }
        :return: Parametres du gimbal
        :rtype: Gimbal

        :raise ValueError: Si dict == None ou si erreur durant validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if args is None:
            raise ValueError('Gimbal args required')

        yaw = args.get('yaw')
        pitch = args.get('pitch')
        roll = args.get('roll')

        if yaw is None and pitch is None and roll is None:
            raise ValueError('No data found in Gimbal args')

        gimbal = Gimbal()

        if yaw is not None:
            gimbal.set_yaw(yaw)

        if pitch is not None:
            gimbal.set_pitch(pitch)

        if roll is not None:
            gimbal.set_roll(roll)

        return gimbal

    def update_from_dict(self, args):
        """
        Modifie un gimbal a partir d'un dictionnaire

        :param args: Dictionnaire representant les donnees a modifier
        :type args: dict
            {
                'yaw'   : value, (optionnal|float|min[-180]|max[180])
                'pitch' : value, (optionnal|float|min[-180]|max[180])
                'roll'  : value  (optionnal|float|min[-180]|max[180])
            }

        :raise ValueError: Si dict == None ou si il n'y as aucune donnees a mettre a jour, ou si erreur de validation
        :raise TypeError: Si erreur de validation du contenu
        """
        if args is None:
            raise ValueError('Gimbal args required')

        yaw = args.get('yaw')
        pitch = args.get('pitch')
        roll = args.get('roll')

        if yaw is None and pitch is None and roll is None:
            raise ValueError('No data found in Gimbal args')

        if yaw is not None:
            self.set_yaw(yaw)

        if pitch is not None:
            self.set_pitch(pitch)

        if roll is not None:
            self.set_roll(roll)

        db.session.add(self)

    def set_yaw(self, yaw):
        """
        Modifie le yaw

        :param yaw: Yaw
        :type yaw: float|string

        :raise ValueError: Si yaw == None ou yaw < -180 ou yaw > 180
        :raise TypeError: Si yaw n'est pas un float et qu'il ne peux pas etre converti en float
        """
        if yaw is None:
            raise ValueError('Gimbal yaw is required')
        if not is_float(yaw):
            raise TypeError('Gimbal yaw have to be a float')
        yaw = float(yaw)
        if yaw < -180 or yaw > 180:
            raise ValueError('Gimbal yaw have to be between -180 and 180')
        self.yaw = yaw

    def set_pitch(self, pitch):
        """
        Modifie le pitch

        :param pitch: Pitch
        :type pitch: float|string

        :raise ValueError: Si pitch == None ou pitch < -180 ou pitch > 180
        :raise TypeError: Si pitch n'est pas un float et qu'il ne peux pas etre converti en float
        """
        if pitch is None:
            raise ValueError('Gimbal pitch is required')
        if not is_float(pitch):
            raise TypeError('Gimbal pitch have to be a float')
        pitch = float(pitch)
        if pitch < -180 or pitch > 180:
            raise ValueError('Gimbal pitch have to be between -180 and 180')
        self.pitch = pitch

    def set_roll(self, roll):
        """
        Modifie le roll

        :param roll: Roll
        :type roll: float|string

        :raise ValueError: Si roll == None ou si roll < -180 ou roll > 180
        :raise TypeError: Si roll n'est pas un floaat et qu'il ne peux pas etre converti en float
        """
        if roll is None:
            raise ValueError('Gimbal roll is required')
        if not is_float(roll):
            raise TypeError('Gimbal roll have to be a float')
        roll = float(roll)
        if roll < -180 or roll > 180:
            raise ValueError('Gimbal roll have to be between -180 and 180')
        self.roll = roll

    def clone(self):
        """
        Retourne une copie du gimbal

        :return: Copie du gimbal
        :rtype: Gimbal
        """
        return Gimbal(yaw=self.yaw, pitch=self.pitch, roll=self.roll)


class DroneParameters(db.Model):
    """
    Classe representant un point de vue / les parametres du drones 
    """
    __tablename__ = 'drone_params'
    id = db.Column(db.Integer, primary_key=True)
    coord_id = db.Column(db.Integer, db.ForeignKey('gps_coord.id'))
    gimbal_id = db.Column(db.Integer, db.ForeignKey('gimbal.id'))
    rotation = db.Column(db.Integer, default=0)

    coord = db.relationship('GPSCoord')
    gimbal = db.relationship('Gimbal')

    @staticmethod
    def from_dict(args):
        """
        Retourne un objet DroneParameters a partir d'un dictionnaire

        :param args: Dictionnaire representant les parametres
        :type  args: dict
            {
                'rotation' : value, (optional|int|min[-180]|max[180]|default[0])
                'coord' :           (required)
                    {
                        'lat' : value, (required|float|min[-90]|max[90])
                        'lon' : value, (required|float|min[-180]|max[180])
                        'alt' : value  (optionnal|float|default[1])
                    }
                'gimbal' :          (optional, else need minimum 1 value)
                    {
                        'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                        'pitch' : value, (optionnal|float|min[-180]|max[180]|default[90])
                        'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
                    }
            }
        :return: Parametres du drone
        :rtype: DroneParameters

        :raise ValueError: Si dict == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if args is None:
            raise ValueError('DroneParameters args required')

        params = DroneParameters()

        if args.get('rotation') is not None:
            params.set_rotation(args.get('rotation'))
        params.set_coord(args.get('coord'))

        if args.get('gimbal') is not None:
            params.set_gimbal(args.get('gimbal'))
        else:
            params.gimbal = Gimbal()

        return params

    def update_from_dict(self, args):
        """
        Modifie les parametres a partir d'un dictionnaire 

        :param args: Dictionnaire representant les parametres
        :type args: dict
            {
                'rotation' : value, (optional|int|min[-180]|max[180])
                'coord' :           (optional)
                    {
                        'lat' : value, (optional|float|min[-90]|max[90])
                        'lon' : value, (optional|float|min[-180]|max[180])
                        'alt' : value  (optional|float|default[1])
                    }
                'gimbal' :          (optional, else need minimum 1 value)
                    {
                        'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                        'pitch' : value, (optionnal|float|min[-180]|max[180]|default[90])
                        'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
                    }
            }
        :raise ValueError: Si dict == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if args is None:
            raise ValueError('DroneParameters args required')

        rotation = args.get('rotation')
        coord = args.get('coord')
        gimbal = args.get('gimbal')

        if rotation is None and coord is None and gimbal is None:
            raise ValueError('No data found in DroneParameters args')

        if rotation is not None:
            self.set_rotation(rotation)

        if coord is not None:
            self.set_coord(coord)

        if gimbal is not None:
            self.set_gimbal(gimbal)

        db.session.add(self)

    def set_rotation(self, rotation):
        """
        Modifie la rotation du drone sur l'axe z

        :param rotation: Rotation du drone sur l'axe z
        :type rotation: int|string

        :raise ValueError: Si rotation == None ou si rotation < -180 ou rotation > 180
        :raise TypeError: Si rotation n'est pas un int et qu'il ne peux pas etre converti en int
        """
        if rotation is None:
            raise ValueError('DroneParameters rotation is required')
        if not is_int(rotation):
            raise TypeError('DroneParameters rotation have to be a int')
        rotation = int(rotation)

        if rotation < -180 or rotation > 180:
            raise ValueError('DroneParameters rotation have to be between -180 and 180')
        self.rotation = rotation

    def set_coord(self, args):
        """
        Modifie la coordonnee

        :param args: Dictionnaire representant la coordonnee GPS
        :type  args: dict
            {
                'lat' : value, (required|float|min[-90]|max[90])
                'lon' : value, (required|float|min[-180]|max[180])
                'alt' : value  (optionnal|float|default[1])
            }

        :raise ValueError: Si dict == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if self.coord is not None:
            self.coord.update_from_dict(args)
        else:
            self.coord = GPSCoord.from_dict(args)

    def set_gimbal(self, args):
        """
        Modifie les parametres du gimbal

        :param args: Dictionnaire representant les parametres du gimbal
        :type args: dict
            {
                'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                'pitch' : value, (optionnal|float|min[-180]|max[180]|default[90])
                'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
            }

        :raise ValueError: Si dict == None ou si erreur durant validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if self.gimbal is not None:
            self.gimbal.update_from_dict(args)
        else:
            self.gimbal = Gimbal.from_dict(args)


class FlightPlan(db.Model):
    """
    Classe representnant un plan de vol
    """
    __tablename__ = 'flightplan'
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, onupdate=datetime.utcnow)
    name = db.Column(db.String(64), unique=True)
    distance = db.Column(db.Float, default=0.0)
    builder_options_id = db.Column(db.Integer, db.ForeignKey('builder_options.id'))
    builder_options = db.relationship('FlightPlanBuilder')

    @staticmethod
    def get_from_id(flightplan_id):
        """
        Retourne un plan de vol a partir de sont identifiant

        :param flightplan_id: Identifiant unique du plan de vol
        :type flightplan_id: int|string

        :return: Plan de vol
        :rtype: FlightPlan

        :raise ValueError: Si id == None ou id <= 0
        :raise TypeError: Si id n'est pas un int et ne peux pas etre converti en int
        """
        if flightplan_id is None:
            raise ValueError('FlightPlan id is required')
        if not is_int(flightplan_id):
            raise TypeError('FlightPlan id have to be a int')
        flightplan_id = int(flightplan_id)

        if flightplan_id <= 0:
            raise ValueError('FlightPlan id must be positive')

        return FlightPlan.query.filter_by(id=flightplan_id).first()

    @staticmethod
    def from_dict(args):
        """
        Retourne un flightplan a partir d'un dictionnaire

        :param args: Dictionnaire representant le flightplan
        :type args: dict
            {
                'name'         : value, (required|string|unique|min_size[3]|max_size[64])
                'created_on' : value  (optional|string|valid_date_format[Y-m-d H:M:S])
            }
        :return: Plan de vol
        :rtype: FlightPlan

        :raise ValueError: Si args == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if args is None:
            raise ValueError('FlightPlan args required')

        flightplan = FlightPlan()
        flightplan.__set_name(args.get('name'))

        created_on = args.get('created_on')
        if created_on is not None:
            if not is_valid_date(created_on, '%Y-%m-%d %H:%M:%S'):
                raise ValueError('Invalid FlightPlan created_on date format')
            flightplan.created_on = datetime.strptime(created_on, '%Y-%m-%d %H:%M:%S')

        return flightplan

    def update_from_dict(self, args):
        """
        Modifie le plan de vol a partir d'un dictionnaire

        :param args: Dictionnaire representant les donnees a modifier
        :type args: dict
            {
                'name'  : value, (optional|string|unique|min_size[3]|max_size[64])
                'waypoints'      (optional)
                    [
                        {
                            'date_created'' : value, (optional|string|valid_date_format[Y-m-d H:M:S])
                            'number'        : value, (required|int|min[0]|max[99]|not_exist)
                            'params'        : {      (required) 
                                'rotation' : value,     (optional|int|min[-180]|max[180]|default[0])
                                'coord' :               (required)
                                    {
                                        'lat' : value,      (required|float|min[-90]|max[90])
                                        'lon' : value,      (required|float|min[-180]|max[180])
                                        'alt' : value       (optionnal|float|default[1])
                                    }
                                'gimbal' :              (optional, else need minimum 1 value)
                                    {
                                        'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                                        'pitch' : value, (optionnal|float|min[-180]|max[180]|default[90])
                                        'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
                                    }
                        }

                    ]
            }

        :raise ValueError: Si dict == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if args is None:
            raise ValueError('FlightPlan args required')

        name = args.get('name')
        waypoints = args.get('waypoints')

        if name is None and waypoints is None:
            raise ValueError('No data found in FlightPlan args')

        if name is not None:
            self.__set_name(name)
        if waypoints is not None:
            self.__set_waypoints(waypoints)

        db.session.add(self)

    def update_informations(self):
        """
        Met a jour les informations du plan de vol tel que la distance
        """
        distance = 0.0
        for i in range(1, self.waypoints.count()):
            distance += self.waypoints[i].parameters.coord.pythagore_distance_to(self.waypoints[i-1].parameters.coord)
        self.distance = distance

    def __set_waypoints(self, w_array):
        """
        Definie les waypoints du plan de vol

        :param w_array: Tableau des waypoint
        :type w_array: dict
            [
                {
                    'date_created'' : value, (optional|string|valid_date_format[Y-m-d H:M:S])
                    'number'        : value, (required|int|min[0]|max[99]|not_exist)
                    'params'        : {      (required) 
                        'rotation' : value,     (optional|int|min[-180]|max[180]|default[0])
                        'coord' :               (required)
                            {
                                'lat' : value,      (required|float|min[-90]|max[90])
                                'lon' : value,      (required|float|min[-180]|max[180])
                                'alt' : value       (optionnal|float|default[1])
                            }
                        'gimbal' :              (optional, else need minimum 1 value)
                            {
                                'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                                'pitch' : value, (optionnal|float|min[-180]|max[180]|default[90])
                                'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
                            }
                }

            ]
        """
        if w_array is None:
            raise ValueError('FlightPlan Waypoint list required')

        if self.waypoints.count() > 0:
            for waypoint in self.waypoints.all():
                waypoint.deep_delete()

            if self.builder_options is not None:
                db.session.delete(self.builder_options)
            db.session.commit()

        for waypoint in w_array:
            waypoint['flightplan_id'] = self.id
            w = Waypoint.from_dict(waypoint)

            db.session.add(w)

        self.update_informations()

    def __set_name(self, name):
        """
        Modifie la nom

        :param name: Nom
        :type name: String

        :raise ValueError: Si name == None ou si len(name) < 3 ou len(name) > 64
        :raise ValueExist: Si un plan de vol porte deja ce nom
        :raise TypeError: Si name n'est pas un string et qu'il ne peut pas en converti en string
        """
        if name is None:
            raise ValueError('FlightPlan name is required')
        if not is_string(name):
            raise TypeError('FlightPlan name have to be a string')
        name = str(name)

        if len(name) < 3 or len(name) > 64:
            raise ValueError('FlightPlan name length have to be between 3 and 64')

        if FlightPlan.query.filter_by(name=name).first() is not None:
            raise ValueError('FlightPlan name already exist')
        self.name = name

    def deep_delete(self):
        """
        Supprime completement un flightplan, waypoint et reconnaissances liees
        """
        for waypoint in self.waypoints.all():
            waypoint.deep_delete()

        db.session.delete(self)


class Waypoint(db.Model):
    """
    Classe representant un point de passage
    """
    __tablename__ = 'waypoint'
    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime, onupdate=datetime.utcnow)
    flightplan_id = db.Column(db.Integer, db.ForeignKey('flightplan.id'))
    number = db.Column(db.Integer)
    parameters_id = db.Column(db.Integer, db.ForeignKey('drone_params.id'))
    parameters = db.relationship('DroneParameters', backref='waypoint')
    flightplan = db.relationship('FlightPlan', backref=db.backref('waypoints', lazy='dynamic'))

    @staticmethod
    def from_dict(args):
        """
        Retourne un waypoint a partir d'un dictionnaire

        :param args: Dictionnaire representant le waypoint
        :type  args: dict
            {
                'flightplan_id' : value, (required|int|exist[flightplan.id])
                'created_on''   : value, (optional|string|valid_date_format[Y-m-d H:M:S])
                'number'        : value, (required|int|min[0]|max[98]|not_exist)
                'parameters'        : {      (required) 
                    'rotation' : value,     (optional|int|min[-180]|max[180]|default[0])
                    'coord' :               (required)
                        {
                            'lat' : value,      (required|float|min[-90]|max[90])
                            'lon' : value,      (required|float|min[-180]|max[180])
                            'alt' : value       (optionnal|float|default[1])
                        }
                    'gimbal' :              (optional, else need minimum 1 value)
                        {
                            'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                            'pitch' : value, (optionnal|float|min[-180]|max[180]|default[90])
                            'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
                        }
                }
            }
        :return: Waypoint
        :rtype: Waypoint

        :raise ValueError: Si dict == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if args is None:
            raise ValueError('Waypoint args required')

        waypoint = Waypoint()

        flightplan = FlightPlan.get_from_id(args.get('flightplan_id'))
        if flightplan is None:
            raise ValueError('FlightPlan #' + args.get('flightplan_id') + ' not found')
        waypoint.flightplan_id = flightplan.id
        waypoint.flightplan = flightplan

        waypoint.set_number(args.get('number'))
        waypoint.set_parameters(args.get('parameters'))

        created_on = args.get('created_on')
        if created_on is not None:
            if not is_valid_date(created_on, '%Y-%m-%d %H:%M:%S'):
                raise ValueError('Invalid Waypoint created_on date format')
            waypoint.created_on = datetime.strptime(created_on, '%Y-%m-%d %H:%M:%S')

        return waypoint

    def update_from_dict(self, args):
        """
        Modifie le waypoint a partir d'un dictionnaire

        :param args: Dictionnaire representant les donnees a modifier
        :type args: dict
            {
                'number'        : value, (optional|int|min[0]|max[99]|not_exist)
                'params'        : {      (optional) 
                    'rotation' : value,     (optional|int|min[-180]|max[180]|default[0])
                    'coord' :               (required)
                        {
                            'lat' : value,      (required|float|min[-90]|max[90])
                            'lon' : value,      (required|float|min[-180]|max[180])
                            'alt' : value       (optionnal|float|default[1])
                        }
                    'gimbal' :              (optional, else need minimum 1 value)
                        {
                            'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                            'pitch' : value, (optionnal|float|min[-180]|max[180]|default[90])
                            'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
                        }
                }
        :raise ValueError: Si dict == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if args is None:
            raise ValueError('Waypoint args required')

        number = args.get('number')
        params = args.get('params')

        if number is None and params is None:
            raise ValueError('No data found in Waypoint args')

        if number is not None:
            self.set_number(number)

        if params is not None:
            self.set_parameters(params)
        db.session.add(self)

    def set_number(self, number):
        """
        Modifier le numero du point de passage

        :param number: Numero du point de passage
        :type number: int|string

        :raise ValueError: Si number == None ou number < 0 ou number > 98
        :raise TypeError: Si number n'est pas un int et qu'il ne peux pas etre converti en int
        :raise ValueExist: Si un waypoint portant ce numero existe deja
        """
        if number is None:
            raise ValueError('Waypoint number is required')
        if not is_int(number):
            raise TypeError('Waypoint number have to be a int')
        number = int(number)

        if number < 0 or number > 98:
            raise ValueError('Waypoint number have to be between 0 and 98')

        if self.flightplan_id is not None:
            if Waypoint.query.filter_by(flightplan_id=self.flightplan_id, number=number).first() is not None:
                raise ValueExist('Waypoint #' + str(number) + ' already exist')
        self.number = number

    def set_parameters(self, args):
        """
        Modifie les parametres du drone

        :param args: Dictionnaire representant les parametres du drone
        :type args: dict
            {
                'rotation' : value, (optional|int|min[-180]|max[180]|default[0])
                'coord' :           (required)
                    {
                        'lat' : value, (required|float|min[-90]|max[90])
                        'lon' : value, (required|float|min[-180]|max[180])
                        'alt' : value  (optionnal|float|default[1])
                    }
                'gimbal' :          (optional, else need minimum 1 value)
                    {
                        'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                        'pitch' : value, (optionnal|float|min[-180]|max[180]|default[90])
                        'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
                    }
            }
        :raise ValueError: Si dict == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        try:
            if self.parameters is not None:
                self.parameters.update_from_dict(args)
            else:
                self.parameters = DroneParameters.from_dict(args)
        except Exception as e:
            error = str(e)
            if self.number is not None:
                error += ' in Waypoint N' + str(self.number)
            raise ValueError(error)

    def deep_delete(self):
        """
        Supprime completement un waypoint et les parametres liees
        """
        db.session.delete(self.parameters)
        db.session.delete(self)


class FlightPlanBuilder(db.Model):
    """
    Classe representant un generateur de plan de vol
    """
    __tablename__ = 'builder_options'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(32))
    coord1_id = db.Column(db.Integer, db.ForeignKey('gps_coord.id'))
    coord2_id = db.Column(db.Integer, db.ForeignKey('gps_coord.id'))
    alt_start = db.Column(db.Float, default=1.0)
    alt_end = db.Column(db.Float)
    h_increment = db.Column(db.Float)
    v_increment = db.Column(db.Float)
    d_rotation = db.Column(db.Float, default=1.0)
    d_gimbal_id = db.Column(db.Integer, db.ForeignKey('gimbal.id'))
    coord1 = db.relationship('GPSCoord', foreign_keys=coord1_id)
    coord2 = db.relationship('GPSCoord', foreign_keys=coord2_id)
    d_gimbal = db.relationship('Gimbal')

    @staticmethod
    def from_dict(args):
        """
        Retourne un objet FlightPlanBuilder representant les options du generateur de plan de vol
        
        :param args: Dictionnaire representant les parametres
        :type args: dict
            {
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
                'alt_start'      : value, (optional|float|min[>0|default[1])
                'alt_end'        : value, (required|float|min[>0])
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
        
        :return: Options du generateur
        :rtype: FlightPlanBuilder
        """

        if args is None:
            raise ValueError('FlightPlanBuilder args required')

        builder = FlightPlanBuilder()
        builder.set_coord1(args.get('coord1'))
        builder.set_coord2(args.get('coord2'))

        alt_start = args.get('alt_start')
        if alt_start is not None:
            builder.set_alt_start(alt_start)
        
        builder.set_alt_end(args.get('alt_end'))
        builder.set_h_increment(args.get('h_increment'))
        builder.set_v_increment(args.get('v_increment'))

        d_rotation = args.get('d_rotation')
        if d_rotation is not None:
            builder.set_d_rotation(d_rotation)

        d_gimbal = args.get('d_gimbal')
        if d_gimbal is not None:
            builder.set_d_gimbal(d_gimbal)
        else:
            builder.d_gimbal = Gimbal()

        return builder

    def set_alt_start(self, alt_start):
        """
        Definie l'altitude de depart
        
        :param alt_start: Altitude de depart
        :type alt_start: float
        """

        if alt_start is None:
            raise ValueError('Parameter alt_start is required')
        alt_start = float(alt_start)
        if alt_start <= 0:
            raise ValueError('Parameter alt_start have to be upper 0')
        self.alt_start = alt_start

    def set_alt_end(self, alt_end):
        """
        Definie l'altitude de d'arrivee

        :param alt_end: Altitude de d'arrivee
        :type alt_end: float
        """

        if alt_end is None:
            raise ValueError('Parameter alt_end is required')
        alt_end = float(alt_end)
        if alt_end <= 0:
            raise ValueError('Parameter alt_end have to be upper 0')
        self.alt_end = alt_end
        
    def set_h_increment(self, h_increment):
        """
        Definie l'increment horizontal

        :param h_increment: Increment horizontal 
        :type h_increment: float
        """

        if h_increment is None:
            raise ValueError('Parameter h_increment is required')
        h_increment = float(h_increment)
        if h_increment <= 0:
            raise ValueError('Parameter h_increment have to be upper 0')
        self.h_increment = h_increment
        
    def set_v_increment(self, v_increment):
        """
        Definie l'increment vertical

        :param v_increment: Increment vertical 
        :type v_increment: float
        """

        if v_increment is None:
            raise ValueError('Parameter v_increment is required')
        v_increment = float(v_increment)
        if v_increment <= 0:
            raise ValueError('Parameter v_increment have to be upper 0')
        self.v_increment = v_increment
        
    def set_d_rotation(self, d_rotation):
        """
        Definie la rotation du drone

        :param d_rotation: Rotation du drone
        :type d_rotation: float
        """

        if d_rotation is None:
            raise ValueError('Parameter d_rotation is required')
        d_rotation = float(d_rotation)
        if d_rotation < -180 or d_rotation > 180:
            raise ValueError('Parameter d_rotation have to be between -180 and 180')
        self.d_rotation = d_rotation

    def set_d_gimbal(self, args):
        """
        Modifie les parametres du gimbal du drone

        :param args: Dictionnaire representant les parametres du gimbal
        :type args: dict
            {
                'yaw'   : value, (optionnal|float|min[-180]|max[180]|default[0])
                'pitch' : value, (optionnal|float|min[-180]|max[180]|default[90])
                'roll'  : value  (optionnal|float|min[-180]|max[180]|default[0])
            }

        :raise ValueError: Si dict == None ou si erreur durant validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if self.d_gimbal is not None:
            self.d_gimbal.update_from_dict(args)
        else:
            self.d_gimbal = Gimbal.from_dict(args)

    def set_coord1(self, args):
        """
        Modifie la coordonnee 1

        :param args: Dictionnaire representant la coordonnee GPS
        :type  args: dict
            {
                'lat' : value, (required|float|min[-90]|max[90])
                'lon' : value, (required|float|min[-180]|max[180])
                'alt' : value  (optionnal|float|default[1])
            }

        :raise ValueError: Si dict == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if self.coord1 is not None:
            self.coord1.update_from_dict(args)
        else:
            self.coord1 = GPSCoord.from_dict(args)

    def set_coord2(self, args):
        """
        Modifie la coordonnee 2

        :param args: Dictionnaire representant la coordonnee GPS
        :type  args: dict
            {
                'lat' : value, (required|float|min[-90]|max[90])
                'lon' : value, (required|float|min[-180]|max[180])
                'alt' : value  (optionnal|float|default[1])
            }

        :raise ValueError: Si dict == None ou si erreur de validation du contenu
        :raise TypeError: Si erreur de validation du contenu
        """
        if self.coord2 is not None:
            self.coord2.update_from_dict(args)
        else:
            self.coord2 = GPSCoord.from_dict(args)
