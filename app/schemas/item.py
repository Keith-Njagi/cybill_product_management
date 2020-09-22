from . import ma

from models.item import ItemModel
from models.brand import BrandModel
from schemas.image import Imagechema

class ItemSchema(ma.SQLAlchemyAutoSchema):
    images = ma.Nested(Imagechema, many=True)
    class Meta:
        model = ItemModel
        load_only = ('brand',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('ItemDetail', id='<id>'),
        'collection': ma.URLFor('ItemList')
    })