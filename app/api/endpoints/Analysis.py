import os
from config import UPLOAD_FOLDER, RESULT_FOLDER
from flask import request, send_from_directory
from flask_restplus import abort
from flask_restplus import Resource
from app.api.serializers.analysis import analysis_data_container, analysis_with_recon, analysis_with_result, analysis_result_with_resources, \
    analysis_post
from app.api import api
from app.extensions import db
from app.models import AppInformations, Analysis, AnalysisResult

ns = api.namespace('analysis', description='Operations related to analysis.')


@ns.route('/')
class AnalysisCollection(Resource):
    @api.marshal_with(analysis_data_container)
    def get(self):
        """
        Get Analysis List
        """

        analysis_list = Analysis.query.all()

        return {'analysis': analysis_list}

    @api.marshal_with(analysis_with_recon, code=201, description='Analysis successfully created.')
    @api.doc(responses={
        400: 'Validation Error'
    })
    @api.expect(analysis_post)
    def post(self):
        """
        Add a Analysis

        201 Success
        400 Validation error
        :return: 
        """
        from app.tasks import run_analysis
        try:
            new_analysis = Analysis.from_dict(request.json)
            db.session.add(new_analysis)
            db.session.commit()

            run_analysis.delay(new_analysis.id)

            return new_analysis, 201

        except Exception as e:
            abort(400, error=str(e))


@ns.route('/<int:id>')
@api.response(404, 'Analysis not found.')
class AnalysisItem(Resource):
    @api.marshal_with(analysis_with_result)
    def get(self, id):
        """
        Get a Analysis

        200 Success
        404 Analysis not found
        :param id: Analysis unique Id
        """

        res = Analysis.query.get_or_404(id)
        return res

    @api.response(204, 'Analysis successfully deleted.')
    def delete(self, id):
        """
        Delete a Analysis

        204 Success
        :param id: Analysis unique Id
        """
        res = Analysis.query.get_or_404(id)
        res.deep_delete()
        db.session.commit()

        return 'Analysis successfully deleted.', 204