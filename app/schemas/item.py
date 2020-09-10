from . import ma

from models.item import ItemModel
from models.brand import BrandModel

class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItemModel
        load_only = ('brand',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('ItemDetail', id='<id>'),
        'collection': ma.URLFor('ItemList')
    })