import os
from config import UPLOAD_FOLDER, RESULT_FOLDER
from flask import request, send_from_directory
from flask_restplus import abort
from flask_restplus import Resource
from app.api.serializers.analysis import analysis_result_with_resources
from app.api import api
from app.extensions import db
from app.models import AppInformations, AnalysisResult

ns = api.namespace('results', description='Operations related to analysis results.')


@ns.route('/<int:id>')
@api.response(404, 'AnalysisResult not found.')
class AnalysisResultItem(Resource):
    @api.marshal_with(analysis_result_with_resources)
    def get(self, id):
        """
        Get a AnalysisResult

        200 Success
        404 AnalysisResult not found
        :param id: AnalysisResult unique Id
        """

        res = AnalysisResult.query.get_or_404(id)
        return res


@ns.route('/<int:id>/content')
@api.response(404, 'AnalysisResult not found.')
class ContentAnalysisResultItem(Resource):
    @api.doc(responses={
        200: 'Success',
        400: 'Analysis have no content'
    })
    def get(self, id):
        """
        Get AnalysisResult content

        200 Success
        404 AnalyisResult not found
        400 AnalysisResult have no content
        :param id: Analysis unique Id
        """

        res = AnalysisResult.query.get_or_404(id)
        if res.filename is None:
            abort(400, error='AnalysisResult have no content')
        path = os.path.join(RESULT_FOLDER, res.filename)

        if not os.path.exists(path) or not os.path.isfile(path):
            abort(400, error='AnalysisResult have no content')

        return send_from_directory(RESULT_FOLDER, res.filename)
