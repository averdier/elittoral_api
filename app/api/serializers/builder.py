from flask_restplus import fields
from app.api import api
from app.api.serializers import minimal_gpscoord, gimbal
from app.api.serializers.waypoint import minimal_waypoint

post_vertical_builder = api.model('VerticalBuilderParams', {
    'flightplan_name' : fields.String(required = True, description = 'FlightPlan name'),
    'coord1' : fields.Nested(minimal_gpscoord, requird = True, description='GPS coord1'),
    'coord2' : fields.Nested(minimal_gpscoord, requird = True, description='GPS coord2'),
    'alt_start' : fields.Float(required = False, description = 'Start altitude of FlightPlan', min = 0, exclusiveMin=True, default = 1),
    'alt_end' : fields.Float(required = True, description = 'End altitude of FlightPlan', min = 0, exclusiveMin=True),
    'h_increment' : fields.Float(required = True, description = 'Horizontal Increment', min = 0, exclusiveMin=True),
    'v_increment' : fields.Float(required = True, description = 'Vertical Increment', min = 0, exclusiveMin=True),
    'd_rotation' : fields.Float(required = False, description = 'Drone rotation', min=-180, max=180, default=0),
    'd_gimbal' : fields.Nested(gimbal, required = False, description = 'Drone Gimbal parameters')
})


builder_output = api.model('BuilderOutput', {
    'name' : fields.String(description = 'Flightplan name', min_length = 3, max_length = 64),
    'waypoints' : fields.List(fields.Nested(minimal_waypoint), description = 'Waypoint list of Flighplan')
})