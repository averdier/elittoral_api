from flask import request
from flask_restplus import abort, marshal
from app.exceptions import ValueExist
from flask_restplus import Resource
from app.api.serializers.flightplan import flightplan, flightplan_complete_with_builder, flightplan_minimal, \
    flightplan_put, flightplan_data_wrapper, flightplan_dump_data_wrapper, flightplan_complete, \
    flightplan_builder_result

from app.core.flightplan_builder import build_vertical_flightplan_from_options
from app.api.serializers.builder import post_vertical_builder
from app.api import api
from app.extensions import db
from app.models import FlightPlan, FlightPlanBuilder, AppInformations

ns = api.namespace('flightplans', description='Operations related to flightplans.')


@ns.route('/dump')
class FlightPlanDump(Resource):
    @api.response(200, 'Success', flightplan_dump_data_wrapper)
    def get(self):
        """
        Get FlightPlans Dump
        """

        result = []
        flightplans = FlightPlan.query.all()

        for fp in flightplans:
            if fp.builder_options is None:
                result.append(marshal(fp, flightplan_complete))
            else:
                result.append(marshal(fp, flightplan_complete_with_builder))

        return {'flightplans': result}


@ns.route('/')
class FlightPlanCollection(Resource):
    @api.marshal_with(flightplan_data_wrapper)
    def get(self):
        """
        Get FlightPlan List
        """

        flightplans = FlightPlan.query.all()

        return {'flightplans': flightplans}

    @api.marshal_with(flightplan, code=201, description='FlightPlan successfully created.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(flightplan_minimal)
    def post(self):
        """
        Add a FlightPlan

        201 Success
        409 FlightPlan name already exist
        400 Validation error
        :return: 
        """
        try:
            fp = FlightPlan.from_dict(request.json)
            db.session.add(fp)
            AppInformations.update()
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
        Get a FlightPlan

        200 Success
        :param id: FlightPlan unique Id
        """
        fp = FlightPlan.query.get_or_404(id)
        if fp.builder_options is None:
            return marshal(fp, flightplan_complete)
        else:
            return marshal(fp, flightplan_complete_with_builder)

    @api.response(204, 'FlightPlan successfully updated.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(flightplan_put)
    def put(self, id):
        """
        Update a FlightPlan

        204 Success
        409 Unique value already exist
        400 Validation error
        :param id: FlightPlan unique Id
        """
        fp = FlightPlan.query.get_or_404(id)

        try:
            fp.update_from_dict(request.json)

            if request.json.get('builder_options') is not None:

                builder_options = FlightPlanBuilder.from_dict(request.json.get('builder_options'))
                flightplan_path = build_vertical_flightplan_from_options(builder_options)

                fp.delete_waypoints()
                fp.waypoints = flightplan_path
                fp.builder_options = builder_options
                fp.update_informations()
                fp.builded = True

                db.session.add(fp)
                db.session.commit()

            return 'FlightPlan successfully updated.', 204

        except ValueExist as e:
            abort(409, error=str(e))
        except ValueError as e:
            abort(400, error=str(e))

    @api.response(204, 'FlightPlan successfully deleted.')
    def delete(self, id):
        """
        Delete a FlightPlan

        204 Success
        :param id: FlightPlan unique Id
        """
        fp = FlightPlan.query.get_or_404(id)
        fp.deep_delete()
        db.session.commit()

        return 'FlightPlan successfully deleted.', 204


@ns.route('/build')
class FlightBuilder(Resource):
    @api.marshal_with(flightplan_builder_result)
    @api.expect(post_vertical_builder)
    def post(self):
        """
        Build vertical FlightPlan
        """

        try:
            fp_name = request.json.get('flightplan_name')
            if FlightPlan.query.filter_by(name=fp_name).first() is not None:
                abort(409, error='FlightPlan name already exist')

            builder = FlightPlanBuilder.from_dict(request.json)

            flightplan_path = build_vertical_flightplan_from_options(builder)

            fp = FlightPlan(
                name=fp_name,
                waypoints=flightplan_path,
                builder_options=builder,
                builded = True
            )

            fp.update_informations()

            if request.json.get('save'):
                db.session.add(fp)
                AppInformations.update()
                db.session.commit()

            return fp
        except Exception as e:
            abort(400, error=str(e))
