from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, BigInteger
from sqlalchemy.dialects import postgresql
from pyhackers.db import DB as db
from pyhackers.common import format_date

class Message(db.Model):
    __tablename__ = "sweet_post"

    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer)
    user_nick = Column(String)
    reply_to_id = Column(String)
    reply_to_uid = Column(String)
    reply_to_uname = Column(String())
    ext_id = Column(String())
    ext_reply_id = Column(String())

    slug = Column(Text)
    content = Column(Text())
    content_html = Column(Text())
    lang = Column(String(length=3))

    mentions = Column(postgresql.ARRAY(String))
    urls = Column(postgresql.ARRAY(String))
    tags = Column(postgresql.ARRAY(String))
    media = Column(postgresql.ARRAY(String))

    has_url = Column(Boolean)
    has_channel = Column(Boolean)

    karma = Column(Float())
    up_votes = Column(Integer())
    down_votes = Column(Integer())
    favorites = Column(Integer())

    published_at = Column(DateTime)

    channel_id = Column(Integer, index=True)

    channels = Column(postgresql.ARRAY(String))

    spam = Column(Boolean)
    flagged = Column(Boolean)

    deleted = Column(Boolean)

    __user = None

    def get_user(self):
        return self.__user

    def set_user(self, val):
        self.__user = val

    def json(self, date_converter=format_date):
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
        return str(self.json())