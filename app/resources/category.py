from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

from models.category import CategoryModel
from schemas.category import CategorySchema
from user_functions.record_user_log import record_user_log


api = Namespace('category', description='Category Management')

category_model = api.model('Category', {
    'name': fields.String(required=True, )
})
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

@api.route('')
class CategoryList(Resource):
    @classmethod
    def get (cls):
        categories = CategoryModel.fetch_all()
        if categories:
            return categories_schema.dump(categories), 200
        return {'message':'There are no categories created yet.'}, 404

    @classmethod
    @api.expect(category_model)
    # @jwt_required
    def post(cls):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not authorised to use this resource'}, 403
        try:
            data = api.payload
            if not data:
                return {'message': 'No input data detected.'}, 400

            name = data['name'].lower()
            if name == '':
                    return {'message': 'You have not specified any key.'}, 400
            
            category = CategoryModel.fetch_by_name(name=name)
            if category:
                return {'message': 'This category already exists.'}, 400

            category = CategoryModel(name=name)
            category.insert_record()

            # Record this event in user's logs
            log_method = 'post'
            log_description = f'Added category <{name}>'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)
            return {'category':name}, 201
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not save category to database.'}, 500


@api.route('/<int:id>')
@api.param('id', 'The Category idenifier')
class CategoryDetail(Resource):
    @classmethod
    def get (cls, id:int):
        category = CategoryModel.fetch_by_id(id)
        if category:
            return category_schema.dump(category), 200
        return {'message':'This category does not exist.'}, 404

    @classmethod
    # @jwt_required
    @api.expect(category_model)
    def put(self, id:int):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not authorised to use this resource.'}, 403
        try:
            data = api.payload
            if not data:
                return {'message': 'No input data detected'}, 400

            name = data['name']

            if name == '':
                return {'message': 'You have not specified any name.'}, 400

            category = CategoryModel.fetch_by_id(id)
            if category:
                category_by_name = CategoryModel.fetch_by_name(name=name)
                if category_by_name:
                    if category_by_name.id != id:
                        return {'message':'This category already exists in another record.'}, 400
                CategoryModel.update(id, name=name) 

                # Record this event in user's logs
                log_method = 'put'
                log_description = f'Updated category <{id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return category_schema.dump(category), 200 # Perform future checks
            return {'message': 'This category does not exist.'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not save category to database.'}, 500

    @classmethod
    # @jwt_required
    def delete(cls, id:int):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not authorised to use this resource'}, 403
        try:
            category = CategoryModel.fetch_by_id(id)
            if category:
                CategoryModel.delete_by_id(id)

                # Record this event in user's logs
                log_method = 'delete'
                log_description = f'Deleted category <{id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return {'message':f'Deleted category <{id}>'}, 200
            return {'message':'This record does not exist'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not delete category.'}, 500

