from flask import request
from flask_restplus import abort
from app.exceptions import ValueExist
from flask_restplus import Resource
from app.api.serializers.recon import recon_post, recon, recon_data_wrapper
from app.api import api
from app.extensions import db
from app.models import Recon

ns = api.namespace('recons', description='Operations related to recons.')


@ns.route('/')
class ReconCollection(Resource):
    @api.marshal_with(recon_data_wrapper)
    def get(self):
        """
        Retourne la liste des reconnaissances
        <!> A revoir pour integrer &flightplan_id = 

        200
        :return: 
        """
        return {'recons': Recon.query.all()}

    @api.marshal_with(recon, code=201, description='Recon successfully created.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(recon_post)
    def post(self):
        """
        Ajoute une reconnaissance

        201 si succes
        400 si erreur de validation
        :return: 
        """
        try:
            rc = Recon.from_dict(request.json)
            db.session.add(rc)
            db.session.commit()

            return rc, 201

        except ValueError as e:
            abort(400, error=str(e))


@ns.route('/<int:id>')
@api.response(404, 'Recon not found.')
class ReconItem(Resource):
    @api.marshal_with(recon)
    def get(self, id):
        """
        Retourne une reconnaissance

        200
        :param id: 
        :return: 
        """
        rc = Recon.query.get_or_404(id)
        return rc

    @api.response(204, 'Recon successfully deleted.')
    def delete(self, id):
        """
        Supprime une reconnaissance

        204 success
        :param id: 
        :return: 
        """
        rc = Recon.query.get_or_404(id)
        rc.deep_delete()
        db.session.commit()

        return 'Recon successfully deleted.', 204
