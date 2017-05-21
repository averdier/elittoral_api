from flask_restplus import fields
from app.api import api
from app.api.serializers.resource import resource

recon_post = api.model('ReconPost', {
    'flightplan_id' : fields.Integer(required = True, description = 'FlightPlan unique ID'),
    'created_on' : fields.DateTime(dt_format='iso8601', required = False, description = 'Datetime of waypoint creation (iso8601)'),
})

recon = api.inherit('Recon', recon_post, {
    'id' : fields.Integer(required=True, description='Recon unique ID'),
    'resources_count' : fields.Integer(attribute=lambda x: x.resources.count() if (x is not None) else None),
})

recon_with_resources = api.inherit('ReconWithResources', recon, {
    'resources' : fields.List(fields.Nested(resource), description="Recon Resources list")
})

recon_data_wrapper = api.model('ReconDataWrapper', {
    'recons' : fields.List(fields.Nested(recon), description='List of Recons')
})
