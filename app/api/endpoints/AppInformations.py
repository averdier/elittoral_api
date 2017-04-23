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

    @api.response(200, 'Success', app_informations)
    def get(self) -> object:
        """
        Retourne les informations de l'application
        """

        app_info = AppInformations.query.first()
        if app_info is None:
            app_info = AppInformations()
            db.session.add(app_info)
            db.session.commit()

        return app_info

