from datetime import datetime as dt
import logging
from pyhackers.db import DB as db
from pyhackers.model.action import Action, ActionType
from pyhackers.model.cassandra.hierachy import ProjectFollower, UserProject


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