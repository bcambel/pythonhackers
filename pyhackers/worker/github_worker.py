import logging
from pyhackers.model.user import User, SocialUser
from pyhackers.model.cassandra.hierachy import (
    User as CsUser, Post as CsPost, UserPost as CsUserPost, UserFollower as CsUserFollower,
    UserTimeLine)


class RegistrationGithubWorker():
    """
    Once a user registers via GitHub, we will fetch the stars/watching projects
    following users/followers
    """

    def __init__(self, user_id, social_account_id):
        self.user_id = user_id
        self.social_account_id = social_account_id
        self.access_token = None

    def get_user_details_from_db(self):
        user = User.query.get(self.user_id)
        social_account = SocialUser.query.get(self.social_account_id)
        self.access_token = social_account.access_token

    def run(self):
        self.get_user_details_from_db()
        pass


def new_github_registration(user_id, social_account_id):
    logging.warn("[TASK][new_github_registration]: [UserId:{}] [SAcc:{}]".format(user_id, social_account_id))

    RegistrationGithubWorker(user_id,social_account_id).run()