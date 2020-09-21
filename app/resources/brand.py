
from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity

from models.brand import BrandModel
from models.category import CategoryModel
from schemas.brand import BrandSchema
from user_functions.record_user_log import record_user_log
from user_functions.validate_logo import allowed_file

api = Namespace('brand', description='Brand Management')

brand_model = api.model('Brand', {
    'name': fields.String(required=True, ),
    'category_id': fields.Integer(required=True,)
})

upload_parser = api.parser()
upload_parser.add_argument('logo', location='files', type=FileStorage, required=True, help='Brand Logo') # location='headers'
upload_parser.add_argument('name', location='form', type=str, required=True, help='Name')
upload_parser.add_argument('category_id', location='form', type=int, required=True, help='Category ID')

logo_parser = api.parser()
logo_parser.add_argument('logo', location='files', type=FileStorage, required=True, help='Brand Logo') # location='headers'

brand_schema = BrandSchema()
brands_schema = BrandSchema(many=True)

@api.route('')
class BrandList(Resource):
    @classmethod
    def get (cls):
        brands = BrandModel.fetch_all()
        if brands:
            return brands_schema.dump(brands), 200
        return {'message':'There are no brands created yet.'}, 404

    @classmethod
    @jwt_required
    @api.expect(upload_parser)
    def post(cls):
        claims = get_jwt_claims()
        try:
            if claims['is_admin']:
                args = upload_parser.parse_args()
                name = args['name'].lower()
                category_id = args['category_id']

                image_file = args.get('logo')  # This is FileStorage instance

                if name == '':
                    return {'message':'You never included a name.'}, 400

                category = CategoryModel.fetch_by_name(id= category_id)
                if category:
                    brand = BrandModel.fetch_by_name(name=name)
                    if brand:
                        return {'message':'This brand already exists.'}, 400

                    if image_file.filename == '':
                        return {'message':'No logo was found.'}, 400
                        
                    if image_file and allowed_file(image_file.filename):
                        logo = secure_filename(image_file.filename)
                        image_file.save(os.path.join( 'uploads', logo))

                        new_brand = BrandModel(logo=logo,name=name, category_id=category_id)
                        new_brand.insert_record()

                        # Record this event in user's logs
                        log_method = 'post'
                        log_description = f'Added brand <{name}> to category <{category_id}>'
                        authorization = request.headers.get('Authorization')
                        auth_token  = {"Authorization": authorization}
                        record_user_log(auth_token, log_method, log_description)

                        return {'brand':name}, 201
                    return {'message':'The logo you uploaded is not recognised.'}, 400
                return {'message': 'The specified category does not exist for this brand!'}, 400
            return {'message':'You are not authorised to use this resource!'}, 403

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not save brand to database.'}, 500

@api.route('/<int:id>')
@api.param('id', 'The brand identifier')
class BrandDetail(Resource):
    @classmethod
    def get(cls, id:int):
        brand = BrandModel.fetch_by_id(id)
        if brand:
            return brand_schema.dump(brand), 200
        return {'message':'This brand does not exist.'}, 404

    @classmethod
    @jwt_required
    @api.expect(brand_model)
    def put(cls, id:int):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not authorised to use this resource'}, 403
        try:
            data = api.payload
            if not data:
                return {'message': 'No input data detected'}, 400

            name = data['name'].lower()
            category_id = data['category_id']

            if name == '':
                return {'message': 'You have not specified any name.'}, 400
            brand = BrandModel.fetch_by_id(id)
            if brand:
                category = CategoryModel.fetch_by_id(id=category_id)
                if category:
                    brand_by_name = BrandModel.fetch_by_name(name=name)
                    if brand_by_name:
                        if brand_by_name.id != id:
                            return {'message':'This brand already exists in another record.'}, 400
                    BrandModel.update(id, name=name, category_id=category_id) 

                    # Record this event in user's logs
                    log_method = 'put'
                    log_description = f'Updated brand <{id}>'
                    authorization = request.headers.get('Authorization')
                    auth_token  = {"Authorization": authorization}
                    record_user_log(auth_token, log_method, log_description)
                    return brand_schema.dump(brand), 200 # Perform future checks
                return {'message': 'This category does not exist.'}, 404
            return {'message':'This brand does not exist.'}, 404  
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not save brand to database.'}, 500


    @classmethod
    @jwt_required
    def delete(cls, id:int):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'You are not authorised to use this resource'}, 403
        try:
            brand = BrandModel.fetch_by_id(id)
            if brand:
                BrandModel.delete_by_id(id)

                # Record this event in user's logs
                log_method = 'delete'
                log_description = f'Deleted brand <{id}>'
                authorization = request.headers.get('Authorization')
                auth_token  = {"Authorization": authorization}
                record_user_log(auth_token, log_method, log_description)
                return {'message':f'Deleted brand <{id}>'}, 200
            return {'message':'This record does not exist'}, 404
        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not delete category.'}, 500



@api.route('/logo/<int:id>')
@api.param('id', 'The brand identifier')
class LogoDetail(Resource):
    @classmethod
    @jwt_required
    @api.expect(logo_parser)
    def put(cls, id:int):
        claims = get_jwt_claims()
        try:
            if claims['is_admin']:
                args = upload_parser.parse_args()
                image_file = args.get('logo')  # This is FileStorage instance

                brand = BrandModel.fetch_by_id(id)
                if brand:
                    if image_file.filename == '':
                        return {'message':'No logo was found.'}, 400
                        
                    if image_file and allowed_file(image_file.filename):
                        logo = secure_filename(image_file.filename)
                        image_file.save(os.path.join( 'uploads', logo))

                        BrandModel.update_logo(id=id,logo=logo)
                        
                        # Record this event in user's logs
                        log_method = 'put'
                        log_description = f'Added brand <{id}> logo'
                        authorization = request.headers.get('Authorization')
                        auth_token  = {"Authorization": authorization}
                        record_user_log(auth_token, log_method, log_description)

                        return brand_schema.dump(brand), 200
                    return {'message':'The logo you uploaded is not recognised.'}, 400
                return {'message':'This brand does not exist.'}, 404                    
            return {'message':'You are not authorised to use this resource!'}, 403

        except Exception as e:
            print('========================================')
            print('Error description: ', e)
            print('========================================')
            return{'message':'Could not save brand logo to database.'}, 500
