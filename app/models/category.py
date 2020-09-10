from datetime import datetime
from typing import List

from . import db

class CategoryModel(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow(), nullable=True)

    brands = db.relationship('BrandModel', lazy='dynamic')


    def insert_record(self) -> None:
        db.session.add(self)
        db.session.commit()
        
    @classmethod
    def fetch_all(cls) -> List['CategoryModel']:
        return cls.query.order_by(cls.id.asc()).all()

    @classmethod
    def fetch_by_id(cls, id:int) -> 'CategoryModel':
        return cls.query.get(id)

    @classmethod
    def fetch_by_name(cls, name:str) -> 'CategoryModel':
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
        

