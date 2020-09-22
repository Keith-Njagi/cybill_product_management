from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

from models.item import ItemModel
from models.brand import BrandModel
from schemas.item import ItemSchema
from user_functions.record_user_log import record_user_log

api = Namespace('item', description='Item Management')

item_model = api.model('Item', {
    'name': fields.String(required=True, description='Name',),
    'brand_id': fields.Integer(required=True, description='Brand ID',),
    'description': fields.String(required=True, description='Description',),
    'price': fields.Float(required=True, description='Price',)
})

item_schema = ItemSchema()
items_schema = ItemSchema(many=True)

@api.route('')
class ItemList(Resource):
    @classmethod
    def get(cls):
        try:
            items = ItemModel.fetch_all()
            if items:
                return items_schema.dump(items), 200
            return {'message':'There are no items created yet.'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch items.'}, 500
        
    @classmethod
    @jwt_required
    @api.expect(item_model)
    def post(cls):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message':'You are not authorised to use this resource'}, 403
        try:
            data = api.payload
            if not data:
                return {'message': 'No input data detected'}, 400

            brand_id = data['brand_id']
            brand = BrandModel.fetch_by_id(id=brand_id)
            if not brand:
                return {'message':'This brand does not exist.'}, 400

            name = data['name'].lower()
            item_by_name = ItemModel.fetch_by_name(name)
            if item_by_name:
                return {'message':'This item already exists.'}, 400

            description = data['description']
            price = data['price']

            new_item = ItemModel(name=name, brand_id=brand_id, description=description, price=price)
            new_item.insert_record()

            # Record this event in user's logs
            log_method = 'post'
            log_description = f'Added item <{name}>'
            authorization = request.headers.get('Authorization')
            auth_token  = {"Authorization": authorization}
            record_user_log(auth_token, log_method, log_description)

            item = ItemModel.fetch_by_name(name)
            return item_schema.dump(item), 201
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not save item to database.'}, 500
        

@api.route('/<int:id>')
class ItemDetail(Resource):
    @classmethod
    def get(cls, id:int):
        try:
            item = ItemModel.fetch_by_id(id)
            if item:
                return item_schema.dump(item), 200
            return {'message':'This item does not exist.'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not fetch item.'}, 500

    @classmethod
    @jwt_required
    @api.expect(item_model)
    def put(cls, id:int):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message':'You are not authorised to use this resource'}, 403
        try:
            data = api.payload
            if not data:
                return {'message': 'No input data detected'}, 400

            item = ItemModel.fetch_by_id(id)
            if item:
                brand_id = data['brand_id']
                brand = BrandModel.fetch_by_id(id=brand_id)
                if not brand:
                    return {'message':'This brand does not exist.'}, 400

                name = data['name'].lower()
                item_by_name = ItemModel.fetch_by_name(name)
                if item_by_name:
                    if item_by_name.id != id:
                        return {'message':'This item already exists.'}, 400

                description = data['description']
                price = data['price']

                ItemModel.update(id=id, name=name, brand_id=brand_id, description=description, price=price)
                
                # Record this event in user's logs
                log_method = 'put'
                log_description = f'Updated item <{id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return item_schema.dump(item), 200
            return {'message':'This item does not exist'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not update item.'}, 500

    @classmethod
    @jwt_required
    def delete(cls, id:int):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not authorised to use this resource'}, 403
        try:
            item = ItemModel.fetch_by_id(id)
            if item:
                ItemModel.delete_by_id(id)

                # Record this event in user's logs
                log_method = 'delete'
                log_description = f'Deleted item <{id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return {'message':f'Deleted item <{id}>'}, 200
            return {'message':'This record does not exist'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not delete item.'}, 500