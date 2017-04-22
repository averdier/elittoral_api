from flask import jsonify, request
from flask_restplus import abort
from app.exceptions import ValueExist
from flask_restplus import Resource
from app.api.business import build_vertical_flightplan
from app.api.serializers.flightplan import flightplan, post_flightplan, put_flightplan, flightplan_data_container
from app.api.serializers.builder import post_vertical_builder, builder_output
from app.api import api
from app.extensions import db
from app.models import FlightPlan

ns = api.namespace('flightplans', description='Operations related to flightplans.')


@ns.route('/')
class FlightPlanCollection(Resource):
    @api.marshal_with(flightplan_data_container)
    def get(self):
        """
        Retourne la liste des plans de vol

        200
        :return: 
        """
        return {'flightplans': FlightPlan.query.all()}

    @api.marshal_with(flightplan, code=201, description='FlightPlan successfully created.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(post_flightplan)
    def post(self):
        """
        Ajoute un plan de vol

        201 si succes
        409 si une valeur unique existe deja
        400 si erreur de validation
        :return: 
        """
        try:
            fp = FlightPlan.from_dict(request.json)
            db.session.add(fp)
            db.session.commit()

            if request.json.get('waypoints') is not None:
                fp.update_from_dict({'waypoints': request.json.get('waypoints')})
                db.session.commit()

            return fp, 201

        except ValueExist as e:
            abort(409, error=str(e))
        except ValueError as e:
            abort(400, error=str(e))


@ns.route('/<int:id>')
@api.response(404, 'Flightplan not found.')
class FlightPlanItem(Resource):
    @api.marshal_with(flightplan)
    def get(self, id):
        """
        Retourne un plan de vol

        200
        :param id: 
        :return: 
        """
        fp = FlightPlan.query.get_or_404(id)
        return fp

    @api.response(204, 'FlightPlan successfully updated.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(put_flightplan)
    def put(self, id):
        """
        Modifie un plan de vol

        204 si succes
        409 si une valeur unique existe deja
        400 si erreur de validation
        :param id: 
        :return: 
        """
        fp = FlightPlan.query.get_or_404(id)

        try:
            fp.update_from_dict(request.json)
            db.session.commit()

            return 'FlightPlan successfully updated.', 204

        except ValueExist as e:
            abort(409, error=str(e))
        except ValueError as e:
            abort(400, error=str(e))

    @api.response(204, 'FlightPlan successfully deleted.')
    def delete(self, id):
        """
        Supprime un plan de vol

        204 success
        :param id: 
        :return: 
        """
        fp = FlightPlan.query.get_or_404(id)
        fp.deep_delete()
        db.session.commit()

        return 'FlightPlan successfully deleted.', 204


@ns.route('/build')
class FlightBuilder(Resource):
    @api.marshal_with(flightplan)
    @api.expect(post_vertical_builder)
    def post(self):
        """
        Retourne un plan de vol vertical
        :return: 
        """
        builder_result = build_vertical_flightplan(request.json)

        fp = FlightPlan(name=builder_result['name'], waypoints = builder_result['waypoints'])

        if request.json.get('save'):
            db.session.add(fp)
            db.session.commit()

        return fp
