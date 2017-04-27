from flask import request
from flask_restplus import abort
from app.exceptions import ValueExist
from flask_restplus import Resource
from app.api.parsers import flightplan_parser
from app.api.serializers.waypoint import minimal_waypoint, post_waypoint, waypoint, waypoint_data_container
from app.api import api
from app.extensions import db
from app.models import Waypoint, AppInformations

ns = api.namespace('waypoints', description='Operations related to waypoints.')


@ns.route('/')
class WaypointCollection(Resource):
    @api.marshal_with(waypoint_data_container)
    @api.expect(flightplan_parser)
    def get(self):
        """
        Get Waypoint list
        
        200 Success
        :return: 
        """

        args = flightplan_parser.parse_args()

        if args['flightplan_id'] is not None:
            result = Waypoint.query.filter_by(flightplan_id = args['flightplan_id'])
        else:
            result = Waypoint.query.all()
        return {'waypoints': result}

    @api.marshal_with(waypoint, code=201, description='Waypoint successfully created.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(post_waypoint)
    def post(self):
        """
        Add a Waypoint

        201 Success
        409 Unique value already exist
        400 Validation error
        :return: 
        """
        try:
            wp = Waypoint.from_dict(request.json)
            wp.flightplan.delete_builder_options()
            db.session.add(wp)
            AppInformations.update()
            db.session.commit()

            return wp, 201

        except ValueExist as e:
            abort(409, error=str(e))
        except ValueError as e:
            abort(400, error=str(e))


@ns.route('/<int:id>')
@api.response(404, 'Waypoint not found.')
class WaypointItem(Resource):
    @api.marshal_with(waypoint)
    def get(self, id):
        """
        Get a Waypoint

        200 Success
        404 Waypoint not found
        :param id: Waypoint unique Id
        """
        wp = Waypoint.query.get_or_404(id)
        return wp

    @api.response(204, 'Waypoint successfully updated.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(minimal_waypoint)
    def put(self, id):
        """
        Update a Waypoint

        204 Success
        404 Waypoint not found
        409 Unique value already exist
        400 Validation error
        :param id: Waypoint unique Id
        """
        wp = Waypoint.query.get_or_404(id)

        try:
            wp.update_from_dict(request.json)
            db.session.commit()

            return 'Waypoint successfully updated.', 204

        except ValueExist as e:
            abort(409, error=str(e))
        except ValueError as e:
            abort(400, error=str(e))

    @api.response(204, 'Waypoint successfully deleted.')
    def delete(self, id):
        """
        Delete a Waypoint

        204 Success
        404 Waypoint not found
        :param id: Waypoint unique Id
        """
        wp = Waypoint.query.get_or_404(id)
        wp.deep_delete()
        db.session.commit()

        return 'Waypoint successfully deleted.', 204
