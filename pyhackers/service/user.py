import logging
from pyhackers.model.user import SocialUser, User
from pyhackers.model.os_project import OpenSourceProject
from pyhackers.db import DB as db
from pyhackers.model.cassandra.hierachy import User as CsUser, UserFollower, UserProject, Project
from pyhackers.apps.idgen import idgen_client


def create_user_from_github_user(access_token, github_user):
    logging.warn("[USER][GITHUB] {}".format(github_user))

    user_login = github_user.get("login")

    social_account = SocialUser.query.filter_by(nick=user_login, acc_type='gh').first()

    user = User.query.filter_by(nick=user_login).first()

    #if user is not None:
    #    return user
    u = user

    if user is None:
        u = User()
        #u.id = idgen_client.get()
        u.nick = user_login
        u.email = github_user.get("email", "")
        u.pic_url = github_user.get("avatar_url")
        name = github_user.get("name", "")
        name_parts = name.split(" ")

        if len(name_parts) > 1:
            u.first_name = name_parts[0]
            u.last_name = " ".join(name_parts[1:])
        else:
            u.last_name = name

    if social_account is None:

        su = SocialUser()
        su.user_id = u.id
        su.nick = user_login
        su.acc_type = 'gh'
        su.email = github_user.get("email", "")
        su.follower_count = github_user.get("followers")
        su.following_count = github_user.get("following")
        su.blog = github_user.get("blog")
        su.ext_id = github_user.get("id")
        su.name = github_user.get("name")
        su.hireable = github_user.get("hireable", False)
        su.access_token = access_token
        u.social_accounts.append(su)

        db.session.add(u)

        try:
            db.session.commit()
        except Exception, e:
            logging.warn(e)
            db.session.rollback()
        finally:
            CsUser.create(id=u.id, nick=u.nick, extended=dict(pic=u.pic_url))

    return u

        # TODO: Create a task to fetch all the other information..

        # starred = user.get_starred()
        # for s in starred:
        #     print s.full_name, s.watchers

        # pub_events = user.get_public_events()

        # for e in pub_events:
        #     print e.id, e.type, e.repo.full_name


def follow_user():
    pass


def load_user(user_id):
    user = User.query.get(user_id)
    followers = UserFollower.filter(user_id=user_id)
    projects = [p.project_id for p in UserProject.filter(user_id=user_id)]
    os_projects = OpenSourceProject.query.filter(OpenSourceProject.id.in_(projects)).all()

    #logging.warn("Projects:%s", )
    #logging.warn("Followers: %s" % [p for p in followers])
    #logging.warn("Act Projects %s" % [p for p in os_projects])

    return user, followers, os_projects


def get_profile(current_user):
    return load_user(current_user.id)


def get_profile_by_nick(nick):
    user = CsUser.filter(nick=nick).first()
    return load_user(user.id)


#from github import Github
#g = Github(access_token,
#           client_id=config.get("github", 'client_id'),
#           client_secret=config.get("github", 'client_secret'), per_page=100)

# user = g.get_user("mitsuhiko")
