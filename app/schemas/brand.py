from . import ma
from models.brand import BrandModel
from models.category import CategoryModel
from models.item import ItemModel
from .item import ItemSchema


class BrandSchema(ma.SQLAlchemyAutoSchema):
    items = ma.Nested(ItemSchema, many=True)
    class Meta:
        model = BrandModel
        load_only = ('category',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('BrandDetail', id='<id>'),
        'collection': ma.URLFor('BrandList')
    })