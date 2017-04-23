from flask_restplus import fields
from app.api import api
from app.api.serializers.waypoint import minimal_waypoint, waypoint_in_flightplan
from app.api.serializers.builder import vertical_builder_options
from app.api.serializers.recon import recon_with_resources

flightplan_minimal = api.model('FlightPlan Minimal', {
    'name' : fields.String(required = True, description = 'Flightplan name', min_length = 3, max_length = 64),
    'created_on' : fields.DateTime(dt_format='iso8601', required = False, description = 'Datetime of FlightPlan creation'),
})

flightplan_post = api.inherit('FlightPlan Post', flightplan_minimal, {
    'waypoints' : fields.List(fields.Nested(minimal_waypoint), description = 'Waypoint list of Flighplan')
})

flightplan_put = api.model('FlightPlan Put', {
    'name' : fields.String(description = 'Flightplan name', min_length = 3, max_length = 64),
    'waypoints' : fields.List(fields.Nested(minimal_waypoint), description = 'Waypoint list of Flighplan')
})

flightplan = api.inherit('FlightPlan', flightplan_minimal, {
    'id' : fields.Integer(required = True, description="FlightPlan unique ID"),
    'updated_on' : fields.DateTime(dt_format='iso8601', required = False, description = 'Last FlightPlan update'),
    'waypoints_count' : fields.Integer(attribute=lambda x: x.waypoints.count()),
    'recons_count' : fields.Integer(attribute=lambda x: x.recons.count()),
    'distance' : fields.Float(required = False, description = 'FlightPlan distance (km)'),
})

flightplan_no_builder = api.inherit('FlightPlan WithoutBuilder', flightplan, {
    'waypoints' : fields.List(fields.Nested(waypoint_in_flightplan), description = 'Waypoint list of Flighplan'),
})

flightplan_with_builder = api.inherit('FlightPlan WithBuilder', flightplan_no_builder, {
    'builder_options' : fields.Nested(vertical_builder_options, description='Builder options if builded', default=None)
})

flightplan_complete = api.inherit('FlightPlan Complete', flightplan_with_builder, {
    'recons' : fields.List(fields.Nested(recon_with_resources), description='Recons list of FlightPlan')
})

flightplan_dump_data_wrapper = api.model('FlightPlan DumpDataWrapper', {
    'flightplans': fields.List(fields.Nested(flightplan_complete))
})

flightplan_data_wrapper = api.model('FlightPlan DataWrapper', {
    'flightplans': fields.List(fields.Nested(flightplan))
})
