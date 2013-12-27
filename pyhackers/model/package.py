__author__ = 'bahadircambel'
from pyhackers.db import DB as db
from pyhackers.utils import nice_number


class Package(db.Model):
    __tablename__ = 'package'

    name = db.Column('name', db.Text, nullable=False,index=True,primary_key=True)
    author = db.Column('author', db.Text, nullable=False)
    author_email = db.Column('author_email', db.Text, nullable=False)
    summary = db.Column('summary', db.Text, nullable=False)
    description = db.Column('description', db.Text, nullable=False)
    url = db.Column('url', db.Text, nullable=False)
    mdown = db.Column('mdown', db.Integer, nullable=False)
    wdown = db.Column('wdown', db.Integer, nullable=False)
    ddown = db.Column('ddown', db.Integer, nullable=False)
    data = db.Column('data', db.Text, nullable=False)

    @property
    def download(self):
        return nice_number(self.mdown)