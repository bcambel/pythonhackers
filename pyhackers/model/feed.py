from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text
from pyhackers.common.stringutils import safe_str
from pyhackers.common.dbfield import Choice
from pyhackers.db import DB as db


FeedStatuses = (
    ('done', 'DONE'),
    ('error', 'ERROR'),
    ('scheduled', 'SCHEDULED'),
    ('moved', 'MOVED'),
    ('nf', "NF"),
    ('?', '?'),
)


class Feed(db.Model):
    __tablename__ = 'feed'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(length=100))
    slug = Column(Text())

    description = Column(Text())
    href = Column(Text)
    link = Column(Text)
    rss = Column(Text)
    rss_hash = Column(Text, index=True)
    lang = Column(String(length=3))
    etag = Column(Text)
    updated = Column(DateTime())
    published = Column(DateTime())
    version = Column(Text)
    author = Column(Text)

    status_code = Column(Integer())
    status = Column(Choice(FeedStatuses))

    last_post = Column(DateTime())
    last_check = Column(DateTime())
    next_check = Column(DateTime())
    active = Column(Boolean())
    top = Column(Boolean())
    news = Column(Boolean())

    logo = Column(Text())

    posts = relationship(Post)


class FeedHistory(db.Model):
    __tablename__ = 'feed_history'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime())
    http_status_code = Column(Integer())  # HTTP Status Code [20x,30x,40x,50x]
    post_count = Column(Integer())
    etag = Column(Text)
    feed_id = Column(Integer())


class Post(db.Model):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(Text())
    author = Column(Text())
    href = Column(Text())
    content_html = Column(Text())
    original_link = Column(Text())
    title_hash = Column(Text, index=True)
    link_hash = Column(Text, index=True)
    post_id = Column(Text())  # most of the time websites publish a URL
    post_id_hash = Column(Text, index=True)
    media = Column(postgresql.ARRAY(String))
    lang = Column(Text)
    tags = Column(postgresql.ARRAY(String))
    published_at = Column(DateTime)
    feed_id = Column(Integer, ForeignKey('feed.id'))

    stats_fb = Column(Integer)
    stats_tw = Column(Integer)

    fetched = Column(Boolean(), default=False)
    indexed = Column(Boolean(), default=False)
    trending = Column(Boolean(), default=False)
    hot = Column(Boolean(), default=False)

    def __repr__(self):
        return "<Post: %s (by %s) %s>" % (safe_str(self.title), self.author, self.href)

    @property
    def original_title(self):
        if hasattr(self, '_original_title'):
            return self._original_title
        else:
            return self.title

    @original_title.setter
    def original_title(self, value):
        self._original_title = value

    @property
    def original_author(self):
        if hasattr(self, '_original_author'):
            return self._original_author
        else:
            return self.author

    @original_author.setter
    def original_author(self, value):
        self._original_author = value