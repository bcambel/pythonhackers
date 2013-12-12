from datetime import datetime as dt
import logging
from pyhackers.db import DB as db
from pyhackers.model.action import Action, ActionType
from pyhackers.model.cassandra.hierachy import ProjectFollower, UserProject
from pyhackers.model.os_project import OpenSourceProject
from pyhackers.service.user import user_list_from_ids


def project_follow(project_id, current_user):
    a = Action()
    a.from_id = current_user.id
    a.to_id = project_id
    a.action = ActionType.FollowProject
    a.created_at = dt.utcnow()

    db.session.add(a)

    success = False
    try:
        db.session.commit()
        success = True
    except Exception, ex:
        db.session.rollback()
        logging.exception(ex)

    if success:
        ProjectFollower.create(project_id=project_id, user_id=current_user.id)
        UserProject.create(project_id=project_id, user_id=current_user.id)


def load_project(slug, current_user):

    project = OpenSourceProject.query.filter_by(slug=slug).first()
    if project is None:
        return

    related_projects = OpenSourceProject.query.filter_by(parent=slug).order_by(
        OpenSourceProject.watchers.desc()).limit(100)

    followers = [f.user_id for f in ProjectFollower.filter(project_id=project.id).limit(20)]
    follower_list = [f for f in user_list_from_ids(followers)]
    print follower_list

    return project, related_projects, follower_list