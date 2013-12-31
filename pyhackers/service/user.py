import logging
from pyhackers.ext.hipchat import notify_registration
from pyhackers.model.user import SocialUser, User
from pyhackers.model.os_project import OpenSourceProject
from pyhackers.model.action import Action, ActionType
from pyhackers.db import DB as db
from pyhackers.model.cassandra.hierachy import User as CsUser, UserFollower, UserFollowing, UserProject, Project
from pyhackers.apps.idgen import idgen_client
from pyhackers.sentry import sentry
import simplejson as json


def create_user_from_github_user(access_token, github_user):
    logging.warn("[USER][GITHUB] {}".format(github_user))

    user_login = github_user.get("login")

    social_account = SocialUser.query.filter_by(nick=user_login, acc_type='gh').first()

    user = User.query.filter_by(nick=user_login).first()

    #if user is not None:
    #    return user
    u = user
    email = github_user.get("email", "")
    name = github_user.get("name", "")

    if user is None:
        u = User()
        #u.id = idgen_client.get()
        u.nick = user_login
        u.email = email
        u.pic_url = github_user.get("avatar_url")

        name_parts = name.split(" ")

        if len(name_parts) > 1:
            u.first_name = name_parts[0] or ""
            u.last_name = " ".join(name_parts[1:])
        else:
            u.last_name = name

    if social_account is None:

        su = SocialUser()

        su.user_id = u.id
        su.nick = user_login
        su.acc_type = 'gh'
        su.email = email
        su.follower_count = github_user.get("followers")
        su.following_count = github_user.get("following")
        su.blog = github_user.get("blog")
        su.ext_id = github_user.get("id")
        su.name = github_user.get("name", "")
        su.hireable = github_user.get("hireable", False)
        su.access_token = access_token
        u.social_accounts.append(su)

        db.session.add(u)

        try:
            db.session.commit()
        except Exception, e:
            logging.warn(e)
            db.session.rollback()
            sentry.captureException()
        finally:
            CsUser.create(id=u.id, nick=u.nick, extended=dict(pic=u.pic_url))
        try:
            notification = u"Id:{} Nick:[{}] Name:[{}] Email:[{}] Followers:{}".format(u.id, user_login, name,
                                                                                   email, github_user.get("followers",0))
            notify_registration(notification)
        except Exception, ex:
            logging.exception(ex)
            sentry.captureException()

    return u

        # TODO: Create a task to fetch all the other information..

        # starred = user.get_starred()
        # for s in starred:
        #     print s.full_name, s.watchers

        # pub_events = user.get_public_events()

        # for e in pub_events:
        #     print e.id, e.type, e.repo.full_name


def follow_user(user_id, current_user):
    if str(user_id) == str(current_user.id):
        logging.warn(u"Don't follow yourself {}".format(user_id))
        return False

    a = Action()
    a.from_id = current_user.id
    a.to_id = user_id
    a.action = ActionType.FollowUser
    db.session.add(a)
    success = False
    try:
        db.session.commit()
        success = True
    except Exception,ex :
        db.session.rollback()

    if success:
        UserFollower.create(user_id=user_id,follower_id=current_user.id)
        UserFollowing.create(user_id=current_user.id, following_id=user_id)

    return success


def user_list_from_ids(ids, dict=True):
    temp_user = CsUser.filter(CsUser.id.in_(set(ids))).limit(50)

    if dict:
        user_list = []
        for u in temp_user:
            d = u._as_dict()
            extras = u.extended
            d.update(**extras)
            user_list.append(d)

        return user_list
    else:
        return temp_user




def load_user(user_id):
    logging.warn("Loading user {}".format(user_id))
    user = User.query.get(user_id)
    followers = [f.follower_id for f in UserFollower.filter(user_id=user_id).limit(20)]
    following = [f.following_id for f in UserFollowing.filter(user_id=user_id).limit(20)]

    projects = [p.project_id for p in UserProject.filter(user_id=user_id)]
    os_projects = OpenSourceProject.query.filter(OpenSourceProject.id.in_(projects)).all()
    cassa_users = user_list_from_ids(set(followers+following), dict=True)

    #print [user for user in csUsers]

    def expand(o):
        #d = o._as_dict()
        #d = d.update(d.get('extended'))
        extras = o.extended
        dict_val = o._as_dict()
        dict_val.update(**extras)
        return dict_val

    user_followers = [filter(lambda x: x.get('id') == user, cassa_users)[0] for user in followers]
    user_following = [filter(lambda x: x.get('id') == user, cassa_users)[0] for user in following]

    return user, user_followers, user_following, os_projects


def get_profile(current_user):
    return load_user(current_user.id)


def get_profile_by_nick(nick):
    user = CsUser.filter(nick=nick).first()
    if user is None:
        return

    return load_user(user.id)





#from github import Github
#g = Github(access_token,
#           client_id=config.get("github", 'client_id'),
#           client_secret=config.get("github", 'client_secret'), per_page=100)

# user = g.get_user("mitsuhiko")
