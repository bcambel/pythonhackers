from sqlalchemy import Boolean,Column, Integer, String, Float, SmallInteger,DateTime, Text
from pyhackers.app import db

class User(db.Model):
    __tablename__		= 'user'

    id 					= Column(Integer, primary_key = True, autoincrement=True)
    nick			    = Column(String(64), unique = True, index=True)
    email 				= Column(String(120), index = True, unique = True)


def new_user(nick,email):
    u = User()
    u.nick = nick
    u.email = email
    db.session.add(u)
    db.session.commit()