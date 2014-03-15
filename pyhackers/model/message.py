from datetime import datetime as dt
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, BigInteger
from sqlalchemy.dialects import postgresql
from sqlalchemy import event
from pyhackers.db import DB as db
from pyhackers.utils import format_date
from pyhackers.model.user import User
from pyhackers.model.channel import Channel


class Message(db.Model):
    __tablename__ = "message"

    id = db.Column(BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship(User)
    user_nick = db.Column(db.String)
    reply_to_id = db.Column(db.String)
    reply_to_uid = db.Column(db.String)
    reply_to_uname = db.Column(db.String)

    ext_id = db.Column(String)
    ext_reply_id = db.Column(String())

    slug = db.Column(Text)
    content = db.Column(Text)
    content_html = db.Column(Text)
    lang = db.Column(String(length=3))

    mentions = db.Column(postgresql.ARRAY(String))
    urls = db.Column(postgresql.ARRAY(String))
    tags = db.Column(postgresql.ARRAY(String))
    media = db.Column(postgresql.ARRAY(String))

    has_url = db.Column(db.Boolean)
    has_channel = db.Column(db.Boolean)

    karma = db.Column(db.Float)
    up_votes = db.Column(db.Integer)
    down_votes = db.Column(db.Integer)
    favorites = db.Column(db.Integer)

    published_at = db.Column(db.DateTime, default=dt.utcnow())

    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), index=True,)
    channel = db.relationship(Channel)
    channels = db.Column(postgresql.ARRAY(String))

    spam = db.Column(db.Boolean, default=False)
    flagged = db.Column(db.Boolean, default=False)

    deleted = db.Column(db.Boolean, default=False)

    def jsonable(self, date_converter=format_date):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'reply_to_id': str(self.reply_to_id),
            'content': self.content,
            'content_html': self.content_html,
            'lang': self.lang,
            'published_at': date_converter(self.published_at),
            'media': self.media,
            'channels': self.channels,
            'mentions': self.mentions,
            "urls": self.urls,
            "tags": self.tags,
        }

    def __str__(self):
        return str(self.jsonable())

from pyhackers.idgen import idgen_client

@event.listens_for(Message, 'before_insert')
def before_inventory_source_insert(mapper, connection, target):
    pass
    #if target.id is None:
    #    target.id = idgen_client.get()