from . import ma
from models.category import CategoryModel
from models.brand import BrandModel
from .brand import BrandSchema

class CategorySchema(ma.SQLAlchemyAutoSchema):
    providers = ma.Nested(BrandSchema, many=True)
    class Meta:
        model = CategoryModel
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.category_category_detail', id='<id>'),
        'collection': ma.URLFor('api.category_category_list')
    })