from flask_restplus import fields
from app.api import api
from app.api.serializers.recon import recon, recon_with_resources, resource

analysis_result = api.model('AnalysisResult', {
    'id': fields.Integer(required=True, description='AnalysisResult unique Id'),
    'created_on': fields.DateTime(dt_format='iso8601', required=True,
                                  description='Datetime of AnalysisResult creation (iso8601)'),
    'analysis_id': fields.Integer(required=True, description='Analysis unique Id'),
    'filename': fields.String(required=True, description='Result filename'),
    'result': fields.Float(required=True, description='Result value'),
    'minuend_resource_id': fields.Integer(required=True, description='Minuend resource unique Id'),
    'subtrahend_resource_id': fields.Integer(required=True, description='Subtrahend resource unique Id')
})

analysis_result_with_resources = api.inherit('AnalysisResut WithResources', analysis_result, {
    'minuend_resource': fields.Nested(resource, required=True, description='Minuend resource'),
    'subtrahend_resource': fields.Nested(resource, required=True, description='Subtrahend resource')
})

analysis_post = api.model('Analysis POST', {
    'minuend_recon_id': fields.Integer(required=True, description='Minuend resource unique Id'),
    'subtrahend_recon_id': fields.Integer(required=True, description='Subtrahend resource unique Id')
})

analysis_base = api.model('Analysis', {
    'id': fields.Integer(required=True, description='Analysis unique Id'),
    'created_on': fields.DateTime(dt_format='iso8601', required=True,
                                  description='Datetime of Analysis creation (iso8601)'),
    'state': fields.String(required=True, description='State of Analysis'),
    'total': fields.Integer(required=True, description='Total resource'),
    'current': fields.Integer(required=True, description='Current number of AnalysisResult'),
    'message': fields.String(required=True, description='Message of analysis task'),
    'result': fields.Float(required=True, description='Result value'),
})

analysis_with_recon = api.inherit('Analysis WithRecon', analysis_base, {
    'minuend_recon': fields.Nested(recon, required=True, description='Minuend recon'),
    'subtrahend_recon': fields.Nested(recon, required=True, description='Subtrahend recon')
})

analysis_with_result = api.inherit('Analysis WithResults', analysis_base, {
    'results' : fields.List(fields.Nested(analysis_result_with_resources), description='List of results')
})

analysis_data_container = api.model('Analysis DataContainer', {
    'analysis': fields.List(fields.Nested(analysis_with_recon), required=True, description='List of analysis')
})
