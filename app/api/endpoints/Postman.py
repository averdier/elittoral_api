from flask import json
from flask_restplus import Resource
from app.api import api

ns = api.namespace('postman', description='Postman export.')

@ns.route('/')
class PostmanExport(Resource):

    def get(self) -> object:
        """
        Get postman dum
        """

        urlvars = False  # Build query strings in URLs
        swagger = True  # Export Swagger specifications
        data = api.as_postman(urlvars=urlvars, swagger=swagger)

        return json.dumps(data)