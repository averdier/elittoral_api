from flask_restplus import fields
from app.api import api
from app.api.serializers import droneparameters

resource_post = api.model('ResourcePost', {
    'recon_id' : fields.Integer(required=True, description='Recon unique ID'),
    'created_on' : fields.DateTime(required=False, description='Resource creation datetime'),
    'number' : fields.Integer(required = True, description = 'Resource number ([0, 98])', min = 0, max = 98),
    'parameters' : fields.Nested(droneparameters, description = 'Parameters of drone')
})

resource = api.inherit('Resource', resource_post, {
    'id' : fields.Integer(required=True, description='Resource unique ID'),
    'filename': fields.String(description='Resource filename')
})


resource_data_wrapper = api.model('ResourceDataWrapper', {
    'resources' : fields.List(fields.Nested(resource), description='List of Resources')
})