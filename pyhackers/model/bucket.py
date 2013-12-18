from sqlalchemy.dialects import postgresql
from pyhackers.db import DB as db
from pyhackers.common import format_date


class Bucket(db.Model):
    __tablename__ = "bucket"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('user.id'), index=True)
    user = db.relationship("User", )
    name = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, nullable=False, index=True)
    created_at = db.Column(db.DateTime)
    follower_count = db.Column(db.Integer)
    projects = db.Column(postgresql.ARRAY(db.String))

    def jsonable(self):
        return {
            'id': unicode(self.id),
            'name': unicode(self.name),
            'slug': unicode(self.slug),
            'created_at': unicode(format_date(self.created_at)),
            'projects': unicode(self.projects),
            'follower_count': unicode(self.follower_count)
        }

    def __repr__(self):
        return str(self.jsonable())

    def __str__(self):
        return str(self.name)
