from datetime import datetime
from typing import List

from . import db

class BrandModel(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    logo = db.Column(db.String(50), nullable=False) # add as foreign key

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    category = db.relationship('CategoryModel')

    items = db.relationship('ItemModel', lazy='dynamic')

    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)


    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()
        
    @classmethod
    def fetch_all(cls) -> List['BrandModel']:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_category(self, category_id:int)-> List['BrandModel']:
        return cls.query.filter_by(category_id=category_id).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'BrandModel':
        return cls.query.get(id)

    @classmethod
    def fetch_by_name(cls, name:str) -> 'BrandModel':
        return cls.query.filter_by(name=name).first()

    @classmethod  
    def update(cls, id, name:str=None, category_id:int=None) -> None:
        record = cls.fetch_by_id(id)
        if name:
            record.name = name
        if category_id:
            record.category_id = category_id
        db.session.commit()

    @classmethod  
    def update_logo(cls, id, logo:str=None) -> None:
        record = cls.fetch_by_id(id)
        if logo:
            record.logo = logo
        db.session.commit()

    @classmethod
    def delete_by_id(cls, id:int) -> None:
        record = cls.query.filter_by(id=id)
        record.delete()
        db.session.commit()
        
