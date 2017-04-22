from flask_restplus import fields
from app.api import api

recon_post = api.model('ReconPost', {
    'flightplan_id' : fields.Integer(required = True, description = 'FlightPlan unique ID'),
    'created_on' : fields.DateTime(dt_format='iso8601', required = False, description = 'Datetime of waypoint creation'),
})

recon = api.inherit('Recon', recon_post, {})

recon_data_wrapper = api.model('ReconDataWrapper', {
    'recons' : fields.List(fields.Nested(recon))
})
