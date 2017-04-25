from flask import request
from flask_restplus import abort, marshal
from app.exceptions import ValueExist
from flask_restplus import Resource
from app.api.business import build_vertical_flightplan
from app.api.serializers.flightplan import flightplan_no_builder, flightplan_with_builder, flightplan_post, \
    flightplan_put, flightplan_data_wrapper, flightplan_dump_data_wrapper, flightplan_complete
from app.api.serializers.builder import post_vertical_builder, builder_output
from app.api import api
from app.extensions import db
from app.models import FlightPlan, FlightPlanBuilder, AppInformations

ns = api.namespace('flightplans', description='Operations related to flightplans.')


@ns.route('/dump')
class FlightPlanDump(Resource):
    @api.response(200, 'Success', flightplan_dump_data_wrapper)
    def get(self):
        """
        Retourne le dump des plans de vols
        """

        result = []
        flightplans = FlightPlan.query.all()

        for fp in flightplans:
            if fp.builder_options is None:
                result.append(marshal(fp, flightplan_no_builder))
            else:
                result.append(marshal(fp, flightplan_with_builder))

        return {'flightplans': result}


@ns.route('/')
class FlightPlanCollection(Resource):

    @api.marshal_with(flightplan_data_wrapper)
    def get(self):
        """
        Retourne la liste des plans de vol
        """

        flightplans = FlightPlan.query.all()

        return {'flightplans': flightplans}

    @api.marshal_with(flightplan_no_builder, code=201, description='FlightPlan successfully created.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(flightplan_post)
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
            AppInformations.update()
            db.session.commit()

            if request.json.get('waypoints') is not None:
                fp.update_from_dict({'waypoints': request.json.get('waypoints')})
                fp.updated_on = None
                db.session.commit()

            return fp, 201

        except ValueExist as e:
            abort(409, error=str(e))
        except ValueError as e:
            abort(400, error=str(e))


@ns.route('/<int:id>')
@api.response(404, 'Flightplan not found.')
class FlightPlanItem(Resource):

    @api.response(200, 'Success', flightplan_complete)
    def get(self, id):
        """
        Retourne un plan de vol

        200
        :param id: 
        :return: 
        """
        fp = FlightPlan.query.get_or_404(id)
        if fp.builder_options is None:
            return marshal(fp, flightplan_no_builder)
        else:
            return marshal(fp, flightplan_with_builder)

    @api.response(204, 'FlightPlan successfully updated.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(flightplan_put)
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
    @api.marshal_with(flightplan_with_builder)
    @api.expect(post_vertical_builder)
    def post(self):
        """
        Retourne un plan de vol vertical
        :return: 
        """
        try:

            builder_result = build_vertical_flightplan(request.json)
            builder = FlightPlanBuilder.from_dict(request.json)

            fp = FlightPlan(name=builder_result['name'], waypoints=builder_result['waypoints'], builder_options=builder)
            fp.update_informations()

            if request.json.get('save'):
                db.session.add(fp)
                AppInformations.update()
                db.session.commit()

            return fp
        except Exception as e:
            abort(400, error=str(e))
