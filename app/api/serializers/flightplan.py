from flask_restplus import fields
from app.api import api
from app.api.serializers.waypoint import minimal_waypoint, waypoint_in_flightplan
from app.api.serializers.builder import vertical_builder_options

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

flightplan_no_builder = api.model('FlightPlan', {
    'id' : fields.Integer(required = True, description="FlightPlan unique ID"),
    'created_on' : fields.DateTime(dt_format='iso8601', required = False, description = 'Datetime of waypoint creation'),
    'name' : fields.String(required = True, description = 'Flightplan name', min_length = 3, max_length = 64),
    'waypoints' : fields.List(fields.Nested(waypoint_in_flightplan), description = 'Waypoint list of Flighplan'),
    'waypoints_count' : fields.Integer(attribute=lambda x: x.waypoints.count()),
})

flightplan_with_builder = api.inherit('FlightPlanWithBuilder', flightplan_no_builder, {
    'builder_options' : fields.Nested(vertical_builder_options, description='Builder options if builded', default=None)
})
