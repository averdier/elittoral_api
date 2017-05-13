from flask import Blueprint
from flask_restplus import Api

blueprint = Blueprint('api', __name__)
api = Api(blueprint,
          title='E-Littoral API',
          version='2.0',
          description='API for the BTS E-Littoral Project')

from app.api.endpoints.AppInformations import ns as info_namespace
from app.api.endpoints.FlightPlans import ns as flightplan_namespace
from app.api.endpoints.Waypoints import ns as waypoint_namespace
from app.api.endpoints.Recons import ns as recon_namespace
from app.api.endpoints.Resources import ns as resource_namespace
from app.api.endpoints.Analysis import ns as analysis_namespace
from app.api.endpoints.Results import ns as result_namespace

api.add_namespace(info_namespace)
api.add_namespace(flightplan_namespace)
api.add_namespace(waypoint_namespace)
api.add_namespace(recon_namespace)
api.add_namespace(resource_namespace)
api.add_namespace(analysis_namespace)
api.add_namespace(result_namespace)
