import logging
from functools import partial
from flask.ext.login import current_user
from flask.ext.admin import Admin, BaseView, expose, Admin, AdminIndexView
from flask.ext.admin.contrib.sqlamodel import ModelView
from pyhackers.model.user import User, SocialUser
from pyhackers.model.os_project import OpenSourceProject
from pyhackers.model.message import Message
from pyhackers.model.channel import Channel
from pyhackers.model.action import Action
from jinja2 import Markup


class ProtectedView(BaseView):
    def is_accessible(self):

        if not current_user.is_authenticated():
            return False

        if hasattr(current_user, "role"):
            logging.warn(u"Checking user.. %s-%s" % (current_user.id, current_user.role))

        if not current_user.role == 0:
            return False

        return True


def truncator(field, ctx, model, name):
    original = getattr(model, field).encode('ascii', 'xmlcharrefreplace')

    truncated = original[:10] if len(original) > 10 else original

    return Markup(u"<span title='{1}' data-role='tooltip'>{0}..</span>".format(truncated, original))


def _href(kls, model, name, url=None):
    original = getattr(model, name)
    title = original.replace("http://", "").replace("https://", "").replace("www", "") \
        .replace("github.com", "")

    if url is not None:
        original = "{}/{}".format(url, original)

    return Markup(u'<a href="{0}" target="_blank">{1}</a>'
    .format(original, title))


def _img(field, ctx, model, name):
    original = getattr(model, field)
    return Markup('<img src="{0}" />'.format(original))


def _nick_href(*args):
    return _href(*args, url='https://github.com')


class ProtectedModelView(ModelView, ProtectedView):
    column_display_pk = True


_desc_trunc = partial(truncator, 'description')
_src_href_ = partial(_href, 'src_url')
_img_img = partial(_img, 'pic_url')


class ProjectModelView(ProtectedModelView):
    column_formatters = {'description': _desc_trunc,
                         'src_url': _href}

    column_searchable_list = ('name', 'description')


class UserModelView(ProtectedModelView):
    column_formatters = {'pic_url': _img_img}
    column_searchable_list = ('nick', 'email', 'first_name', 'last_name')


class SocialUserModelView(ProtectedModelView):
    column_formatters = {'nick': _nick_href}


def init(app, db):
    admin = Admin(app)

    admin.add_view(UserModelView(User, db.session, category='User'))
    admin.add_view(SocialUserModelView(SocialUser, db.session, category='User'))
    admin.add_view(ProjectModelView(OpenSourceProject, db.session, name='Project'))
    admin.add_view(ProtectedModelView(Message, db.session))
    admin.add_view(ProtectedModelView(Action, db.session))
    admin.add_view(ProtectedModelView(Channel, db.session))