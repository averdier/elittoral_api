from flask import Blueprint
from flask_restplus import Api

blueprint = Blueprint('api', __name__)
api = Api(blueprint,
          title='E-Littoral API',
          version='2.0',
          description='API for the BTS E-Littoral Project')

from app.api.endpoints.FlightPlans import ns as flightplan_namespace
from app.api.endpoints.Waypoints import ns as waypoint_namespace

api.add_namespace(flightplan_namespace)
