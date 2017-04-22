from flask_restplus import fields
from app.api import api
from app.api.serializers.waypoint import minimal_waypoint, waypoint_in_flightplan

minimal_flightplan = api.model('MinimalFlightPlan', {
    'name' : fields.String(required = True, description = 'Flightplan name', min_length = 3, max_length = 64)
})

post_flightplan = api.inherit('PostFlightPlan', minimal_flightplan, {
    'created_on' : fields.DateTime(dt_format='iso8601', required = False, description = 'Datetime of waypoint creation'),
    'waypoints' : fields.List(fields.Nested(minimal_waypoint), description = 'Waypoint list of Flighplan')
})

put_flightplan = api.model('PutFlightPlan', {
    'name' : fields.String(description = 'Flightplan name', min_length = 3, max_length = 64),
    'waypoints' : fields.List(fields.Nested(minimal_waypoint), description = 'Waypoint list of Flighplan')
})

flightplan = api.model('FlightPlan', {
    'id' : fields.Integer(required = True, description="FlightPlan unique ID"),
    'created_on' : fields.DateTime(dt_format='iso8601', required = False, description = 'Datetime of waypoint creation'),
    'name' : fields.String(required = True, description = 'Flightplan name', min_length = 3, max_length = 64),
    'waypoints' : fields.List(fields.Nested(waypoint_in_flightplan), description = 'Waypoint list of Flighplan'),
    'waypoints_count' : fields.Integer(attribute=lambda x: x.waypoints.count())
})

flightplan_data_container = api.model('FlightPlanDataContainer', {
    'flightplans' : fields.List(fields.Nested(flightplan))
})