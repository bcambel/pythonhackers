from pyhackers.db import DB as db
from pyhackers.utils import format_date


class Channel(db.Model):
    __tablename__ = "channel"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    slug = db.Column(db.Text, nullable=False, index=True, unique=True)
    created_at = db.Column(db.DateTime)

    post_count = db.Column(db.BigInteger)

    disabled = db.Column(db.Boolean)

    def jsonable(self):
        return {
            'id': unicode(self.id),
            'name': unicode(self.name),
            'slug': unicode(self.slug),
            'post_count': unicode(self.post_count),
            'disabled': unicode(self.disabled),
            'created_at': unicode(format_date(self.created_at)),
        }

    def __repr__(self):
        return str(self.jsonable())

    def __str__(self):
        return str(self.name)

