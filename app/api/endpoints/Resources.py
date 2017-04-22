import os
from config import UPLOAD_FOLDER
from flask import request, send_from_directory
from flask_restplus import abort
from flask_restplus import Resource
from app.exceptions import ValueExist
from app.api.parsers import upload_parser
from app.api.serializers.resource import resource_post, resource_data_wrapper, resource
from app.api import api
from app.extensions import db
from app.models import Resource as ReconResource

ns = api.namespace('resources', description='Operations related to resources.')


@ns.route('/')
class ResourceCollection(Resource):
    @api.marshal_with(resource_data_wrapper)
    def get(self):
        """
        Retourne la liste des ressource
        <!> A revoir pour integrer &recon_id = 

        200
        :return: 
        """
        return {'resources': ReconResource.query.all()}

    @api.marshal_with(resource, code=201, description='Resource successfully created.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(resource_post)
    def post(self):
        """
        Ajoute une ressource

        201 si succes
        400 si erreur de validation
        :return: 
        """
        try:
            res = ReconResource.from_dict(request.json)
            db.session.add(res)
            db.session.commit()

            return res, 201

        except ValueError as e:
            abort(400, error=str(e))


@ns.route('/<int:id>')
@api.response(404, 'Resource not found.')
class ResourceItem(Resource):

    @api.marshal_with(resource)
    def get(self, id):
        """
        Retourne une resource

        200
        :param id: 
        :return: 
        """
        res = ReconResource.query.get_or_404(id)
        return res

    @api.response(204, 'Resource successfully deleted.')
    def delete(self, id):
        """
        Supprime une ressource

        204 success
        :param id: 
        :return: 
        """
        res = ReconResource.query.get_or_404(id)
        res.deep_delete()
        db.session.commit()

        return 'Resource successfully deleted.', 204


@ns.route('/<int:id>/content')
@api.response(404, 'Waypoint not found.')
class ContentResourceItem(Resource):

    @api.marshal_with(resource, code=201, description='Resource content successfully uploaded.')
    @api.expect(upload_parser)
    def post(self, id):
        """
        Ajoute le contenu de la ressource si celui n'existe pas
        """
        res = ReconResource.query.get_or_404(id)
        args = upload_parser.parse_args()
        try:
            res.set_content(args['file'])
            return res

        except ValueExist as e:
            abort(409, error=str(e))

        except ValueError as e:
            abort(400, error=str(e))

    @api.doc(responses={
        200: 'Success',
        400: 'Resource have no content'
    })
    def get(self, id):
        """
        Retourne le contenu de la ressource si il existe

        200
        :param id: 
        :return: 
        """

        res = ReconResource.query.get_or_404(id)
        if res.filename is None:
            abort(400, error='Resource have no content')
        path = os.path.join(UPLOAD_FOLDER, res.filename)

        if not os.path.exists(path) or not os.path.isfile(path):
            abort(400, error='Resource have no content')

        return send_from_directory(UPLOAD_FOLDER, resource.filename)

    @api.response(204, 'Resource content successfully deleted.')
    def delete(self, id):
        """
        Supprime le contenu de la ressource
        """
        res = ReconResource.query.get_or_404(id)
        res.remove_content()
        db.session.commit()

        return 'Resource content successfully deleted.', 204
