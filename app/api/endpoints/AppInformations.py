from flask import request
from flask_restplus import abort, marshal
from flask_restplus import Resource
from app.api.serializers import app_informations
from app.api import api
from app.extensions import db
from app.models import AppInformations

ns = api.namespace('infos', description='App Informations.')


@ns.route('/')
class Informations(Resource):

    @api.marshal_with(app_informations)
    @api.response(200, 'Success', app_informations)
    def get(self) -> object:
        """
        Get current App informations
        """

        app_info = AppInformations.query.filter_by(id = 1).first()
        if app_info is None:
            abort(400, error='No App informations')

        return app_info

