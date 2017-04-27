from flask_restplus import fields
from app.api import api
from app.api.serializers import droneparameters

minimal_waypoint = api.model('MinimalWaypoint', {
    'number' : fields.Integer(required = True, description = 'Waypoint number ([0, 98])', min = 0, max = 98),
    'parameters' : fields.Nested(droneparameters, description = 'Parameters of drone')
})

waypoint_in_flightplan = api.inherit('WaypointInFlightPlan', minimal_waypoint, {
    'id' : fields.Integer(required = True, description = 'Waypoint unique ID')
})

post_waypoint = api.inherit('PostWaypoint', minimal_waypoint, {
    'created_on' : fields.DateTime(dt_format='iso8601', required = False, description = 'Datetime of waypoint creation (iso8601)'),
    'flightplan_id' : fields.Integer(required = True, description = 'Flightplan unique ID', min = 1)
})

waypoint = api.inherit('Waypoint', post_waypoint, {
    'id' : fields.Integer(required = True, description = 'Waypoint unique ID')
})

waypoint_data_container = api.model('WaypointDataContainer', {
    'waypoints' : fields.List(fields.Nested(waypoint), description="List of Waypoints")
})
