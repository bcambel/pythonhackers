import logging
from cqlengine.query import DoesNotExist
from pyhackers.service.post import load_posts
from pyhackers.worker.hipchat import notify_registration
from pyhackers.model.user import SocialUser, User
from pyhackers.model.os_project import OpenSourceProject
from pyhackers.model.action import Action, ActionType
from pyhackers.db import DB as db
from pyhackers.model.cassandra.hierachy import User as CsUser, UserFollower, UserFollowing, UserProject, Project, UserPost, UserDiscussion
from pyhackers.apps.idgen import idgen_client
from pyhackers.sentry import sentry_client
import simplejson as json
from pyhackers.job_scheduler import worker_queue


def create_user_from_github_user(access_token, github_user):
    # FIXME: Unacceptable method. Too long, doing a lot of stuff, error prone, etc..
    # FIXME: Refactor me please. Destruct me

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
            sentry_client.captureException()
        finally:
            CsUser.create(id=u.id, nick=u.nick, extended=dict(pic=u.pic_url))
        try:
            notification = u"Id:{} Nick:[{}] Name:[{}] Email:[{}] Followers:{}".format(u.id, user_login, name,
                                                                                       email,
                                                                                       github_user.get("followers", 0))

            worker_queue.enqueue(notify_registration, args=(notification,), result_ttl=0)
        except Exception, ex:
            logging.exception(ex)
            sentry_client.captureException()

    return u


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
    except Exception, ex:
        db.session.rollback()

    if success:
        UserFollower.create(user_id=user_id, follower_id=current_user.id)
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


def load_user_profiles(user_ids):
    return list(CsUser.objects.filter(id__in=user_ids).allow_filtering())


def load_user(user_id, current_user=None):
    """
    Loads all the details about the user including Followers/Following/OpenSource projects list.
    """
    logging.warn("Loading user {}".format(user_id))
    user = User.query.get(user_id)

    user_followers, user_following = [], []

    # FIXME: This try/except block is ugly as hell. Refactor please!
    try:
        followers = [f.follower_id for f in UserFollower.filter(user_id=user_id).limit(20)]
        following = [f.following_id for f in UserFollowing.filter(user_id=user_id).limit(20)]

        cassa_users = user_list_from_ids(set(followers + following), dict=True)

        def expand(o):
            extras = o.extended
            dict_val = o._as_dict()
            dict_val.update(**extras)
            return dict_val

        user_followers = [filter(lambda x: x.get('id') == u, cassa_users)[0] for u in followers]
        user_following = [filter(lambda x: x.get('id') == u, cassa_users)[0] for u in following]

    except Exception, ex:
        logging.warn(ex)
        sentry_client.captureException()

    return user, user_followers, user_following


def get_profile(current_user):
    return load_user(current_user.id)


def get_profile_by_nick(nick):
    user = None
    exception = False

    try:
        user = CsUser.filter(nick=nick).first()
    except Exception, ex:
        exception = True
        logging.exception(ex)
        sentry_client.captureException()

    if user is None and exception:
        # FIXME: backoff to our Postgres. Field Names are different!
        try:
            user = User.query.filter_by(nick=nick)

            return user, [], [], []
        except:
            return None

    if user is None:
        return None

    return load_user(user.id)


def get_user_projects_by_nick(nick):
    try:
        user = CsUser.filter(nick=nick).first()
    except DoesNotExist, dne:
        user = None

    if user is None:
        return

    projects = [p.project_id for p in UserProject.filter(user_id=user.id)]
    os_projects = OpenSourceProject.query.filter(OpenSourceProject.id.in_(projects)).order_by(
            OpenSourceProject.stars.desc()).all()

    return user, os_projects



def get_user_timeline_by_nick(nick):
    try:
        user = CsUser.filter(nick=nick).first()
    except DoesNotExist, dne:
        user = None

    if user is None:
        return

    posts = [p.post_id for p in UserPost.objects.filter(user_id=user.id).order_by('-post_id').limit(5)]

    return user, reversed(load_posts(posts)or [])


def load_github_data():
    return
    access_token, config = None
    from github import Github
    g = Github(access_token,
               client_id=config.get("github", 'client_id'),
               client_secret=config.get("github", 'client_secret'), per_page=100)

    user = g.get_user("mitsuhiko")
    #TODO: Create a task to fetch all the other information..

    starred = user.get_starred()
    for s in starred:
         print s.full_name, s.watchers

    pub_events = user.get_public_events()

    for e in pub_events:
         print e.id, e.type, e.repo.full_name