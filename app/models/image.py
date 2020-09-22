from datetime import datetime
from typing import List

from . import db

class ImageModel(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String, nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    item = db.relationship('ItemModel')


    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_all(cls) -> List['ImageModel']:
        return cls.query.order_by(cls.price.asc()).all()

    @classmethod
    def fetch_by_item(self, item_id:int)-> List['ImageModel']:
        return cls.query.filter_by(item_id=item_id).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'ImageModel':
        return cls.query.get(id)

    @classmethod
    def fetch_by_name(cls, name:str) -> 'ImageModel':
        return cls.query.filter_by(name=name).first()

    @classmethod  
    def update(cls, id, name:str=None) -> None:
        record = cls.fetch_by_id(id)
        if name:
            record.name = name
        db.session.commit()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        

