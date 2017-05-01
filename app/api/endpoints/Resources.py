import os
from config import UPLOAD_FOLDER, THUMBNAIL_FOLDER
from flask import request, send_from_directory
from flask_restplus import abort
from flask_restplus import Resource
from app.exceptions import ValueExist
from app.api.parsers import upload_parser, recon_parser
from app.api.serializers.resource import resource_post, resource_data_wrapper, resource
from app.api import api
from app.extensions import db
from app.models import AppInformations, Resource as ReconResource

ns = api.namespace('resources', description='Operations related to resources.')


@ns.route('/')
class ResourceCollection(Resource):
    @api.marshal_with(resource_data_wrapper)
    @api.expect(recon_parser)
    def get(self):
        """
        Get Resources list

        200 Success
        """
        args = recon_parser.parse_args()

        if args['recon_id'] is not None:
            result = ReconResource.query.filter_by(recon_id=args['recon_id'])
        else:
            result = ReconResource.query.all()
        return {'resources': result}

    @api.marshal_with(resource, code=201, description='Resource successfully created.')
    @api.doc(responses={
        409: 'Value Exist',
        400: 'Validation Error'
    })
    @api.expect(resource_post)
    def post(self):
        """
        Add a Resource

        201 Success
        400 Validation error
        :return: 
        """
        try:
            res = ReconResource.from_dict(request.json)
            db.session.add(res)
            AppInformations.update()
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
        Get a Resource

        200 Success
        404 Resource not found
        :param id: Resource unique Id
        """
        res = ReconResource.query.get_or_404(id)
        return res

    @api.response(204, 'Resource successfully deleted.')
    def delete(self, id):
        """
        Delete a Resource

        204 Success
        404 Resource not found
        :param id: Resource unique Id
        """
        res = ReconResource.query.get_or_404(id)
        res.deep_delete()
        db.session.commit()

        return 'Resource successfully deleted.', 204


@ns.route('/<int:id>/thumbnail')
@api.response(404, 'Resource not found.')
class ThumbnailResourceItem(Resource):
    @api.doc(responses={
        200: 'Success',
        400: 'Resource have no thumbnail'
    })
    def get(self, id):
        """
        Get Resource content

        200 Success
        404 Resource not found
        400 Resource have no thumbnail
        :param id: Resoure unique Id
        """

        res = ReconResource.query.get_or_404(id)
        if res.filename is None:
            abort(400, error='Resource have no content')

        path = os.path.join(THUMBNAIL_FOLDER, res.filename)

        if not os.path.exists(path) or not os.path.isfile(path):
            abort(400, error='Resource have no thumbnail')

        return send_from_directory(THUMBNAIL_FOLDER, res.filename)


@ns.route('/<int:id>/content')
@api.response(404, 'Resource not found.')
class ContentResourceItem(Resource):
    @api.response(204, 'Resource content successfully uploaded.')
    @api.expect(upload_parser)
    def post(self, id):
        """
        Set Resource content
        
        200 Success
        404 Resource not found
        409 Content already exist
        400 Validation error
        """
        res = ReconResource.query.get_or_404(id)
        args = upload_parser.parse_args()
        try:
            res.set_content(args['file'])

            from app.tasks import task_build_thumbnail
            task_build_thumbnail.delay(id)

            return 'Resource content successfully uploaded.', 204

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
        Get Resource content

        200 Success
        404 Resource not found
        400 Resource have no content
        :param id: Resoure unique Id
        """

        res = ReconResource.query.get_or_404(id)
        if res.filename is None:
            abort(400, error='Resource have no content')
        path = os.path.join(UPLOAD_FOLDER, res.filename)

        if not os.path.exists(path) or not os.path.isfile(path):
            abort(400, error='Resource have no content')

        return send_from_directory(UPLOAD_FOLDER, res.filename)

    @api.response(204, 'Resource content successfully deleted.')
    def delete(self, id):
        """
        Delete Resource content
        
        204 Success
        404 Resource not found
        """
        res = ReconResource.query.get_or_404(id)
        res.remove_content()
        db.session.commit()

        return 'Resource content successfully deleted.', 204
