from sqlalchemy.dialects import postgresql
from pyhackers.db import DB as db


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
    categories = db.Column("categories", postgresql.ARRAY(db.String))

    hide = db.Column("hide", db.Boolean, default=False)
    lang = db.Column("lang", db.SmallInteger, default=0)
    __tablename__ = 'os_project'


    def to_dict(self, **kwargs):
        result = {
            'id' : unicode(self.id),
            'slug' : unicode(self.slug),
            'name' : unicode(self.name),
            'src_url' : unicode(self.src_url),
            'description' : unicode(self.description),
            'watchers': self.watchers
        }

        result.update(**kwargs)
        return result