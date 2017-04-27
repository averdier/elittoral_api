from flask import request
from flask_restplus import abort
from flask_restplus import Resource
from app.api.parsers import flightplan_parser
from app.api.serializers.recon import recon_post, recon, recon_data_wrapper, recon_with_resources
from app.api import api
from app.extensions import db
from app.models import Recon, AppInformations

ns = api.namespace('recons', description='Operations related to recons.')


@ns.route('/')
class ReconCollection(Resource):
    @api.marshal_with(recon_data_wrapper)
    @api.expect(flightplan_parser)
    def get(self):
        """
        Get Recons list

        200 Success
        """
        args = flightplan_parser.parse_args()

        if args['flightplan_id'] is not None:
            result = Recon.query.filter_by(flightplan_id = args['flightplan_id'])
        else:
            result = Recon.query.all()
        return {'recons': result}

    @api.marshal_with(recon, code=201, description='Recon successfully created.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(recon_post)
    def post(self):
        """
        Add a Recon

        201 Success
        400 Validation error
        """
        try:
            rc = Recon.from_dict(request.json)
            db.session.add(rc)
            AppInformations.update()
            db.session.commit()

            return rc, 201

        except ValueError as e:
            abort(400, error=str(e))


@ns.route('/<int:id>')
@api.response(404, 'Recon not found.')
class ReconItem(Resource):
    @api.marshal_with(recon_with_resources)
    def get(self, id):
        """
        Get a Recon

        200 Success
        404 Recon not found
        :param id: Recon unique Id
        """
        rc = Recon.query.get_or_404(id)
        return rc

    @api.response(204, 'Recon successfully deleted.')
    def delete(self, id):
        """
        Delete a Recon

        204 Success
        404 Recon not found
        :param id: Recon unique Id
        """
        rc = Recon.query.get_or_404(id)
        rc.deep_delete()
        db.session.commit()

        return 'Recon successfully deleted.', 204
