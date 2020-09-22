from datetime import datetime
from typing import List

from . import db

class ItemModel(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)

    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))
    brand = db.relationship('BrandModel')


    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column (db.Float(precision=2), nullable=False)

    status = db.Column(db.String, nullable=False, default='available') # 'available' or 'sold out'
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    images = db.relationship('ImageModel')

    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def fetch_all(cls) -> List['ItemModel']:
        return cls.query.order_by(cls.price.asc()).all()

    @classmethod
    def fetch_by_category(self, category_id:int)-> List['ItemModel']:
        return cls.query.filter_by(category_id=category_id).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'ItemModel':
        return cls.query.get(id)

    @classmethod
    def fetch_by_name(cls, name:str) -> 'ItemModel':
        return cls.query.filter_by(name=name).first()

    @classmethod  
    def update(cls, id, name:str=None, description:str=None, price:float=None, status:str=None) -> None:
        record = cls.fetch_by_id(id)
        if name:
            record.name = name
        if description:
            record.description = description
        if price:
            record.price = price
        if status:
            record.status = status
        db.session.commit()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        

