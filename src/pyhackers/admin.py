import logging
from flask.ext.login import current_user
import pytz
from flask.ext.admin import Admin, BaseView, expose, Admin, AdminIndexView
from flask.ext.admin.contrib.sqlamodel import ModelView
from db import DB as db


def init(app):
    from model.user import User, SocialUser

    class ProtectedView(BaseView):
        def is_accessible(self):
            return True
            logging.warn("Checking user.. %s-%s" % (current_user, current_user.role ))

            if not current_user.is_authenticated():
                return False

            if not current_user.role == 'admin':
                return False

            return True


    class ProtectedModelView(ModelView, ProtectedView):
        pass


    class MyView(AdminIndexView, ProtectedView):
        pass


    admin = Admin(app, index_view=MyView())

    admin.add_view(ProtectedModelView(User, db.session, category='User'))
    admin.add_view(ProtectedModelView(SocialUser, db.session, category='User'))