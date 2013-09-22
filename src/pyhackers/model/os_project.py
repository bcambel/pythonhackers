from sqlalchemy import Boolean, Column, Integer, String, Float, SmallInteger, DateTime, Text
from db import DB as db


class OpenSourceProject(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    name = db.Column('name', db.String(100), nullable=False)
    slug = db.Column('slug', db.String(100), unique=True, index=True, nullable=False)
    description = db.Column('description', db.Unicode(500))
    src_url = db.Column('src_url', db.Unicode(200))
    doc_url = db.Column('doc_url', db.Unicode(200))
    stars = db.Column('starts', db.Integer)
    watchers = db.Column('watchers', db.Integer)
    forks = db.Column('forks', db.Integer)
    parent = db.Column("parent", db.String(100), nullable=True, index=True )

    __tablename__ = 'os_project'
