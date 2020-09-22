from . import ma

from models.image import ImageModel
from models.item import ItemModel

class Imagechema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ImageModel
        load_only = ('item',)
        dump_only = ('id', 'created', 'updated',)
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('ImageDetail', id='<id>'),
        'collection': ma.URLFor('ImageList')
    })