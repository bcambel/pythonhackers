from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, BigInteger, SmallInteger
from sqlalchemy.dialects import postgresql
from sqlalchemy import event
from pyhackers.db import DB as db
from pyhackers.common import format_date


class Action(db.Model):
    __tablename__ = "action"

    id = db.Column(db.BigInteger, primary_key=True)
    from_id = db.Column(db.BigInteger, nullable=False)
    to_id = db.Column(db.BigInteger)
    action = db.Column(db.SmallInteger, nullable=False)
    created_at = db.Column(db.DateTime)
    deleted_at = db.Column(db.DateTime)
    deleted = db.Column(db.Boolean, default=False)

    def jsonable(self):
        return {
            'id': unicode(self.id),
            'from_id': unicode(self.from_id),
            'to_id': unicode(self.to_id),
            'action': unicode(self.action),
            'created_at': unicode(format_date(self.created_at)),
            'deleted_at': unicode(format_date(self.deleted_at)),
            'deleted': unicode(self.deleted),
        }

    def __str__(self):
        return str(self.jsonable())

    def __repr__(self):
        return str(self.jsonable())

from pyhackers.idgen import idgen_client

@event.listens_for(Action, 'before_insert')
def before_inventory_source_insert(mapper, connection, target):
    target.id = idgen_client.get()


class ActionType():

    FollowProject = 1
    UnFollowProject = 2