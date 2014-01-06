import sys
import logging
from cqlengine.management import sync_table, create_keyspace
import argparse
import textwrap


def create(cassa_keyspace='pyhackers'):
    assert cassa_keyspace != '' or cassa_keyspace is not None

    logging.warn("Creating/Sync'ing {}".format(cassa_keyspace))

    create_keyspace(cassa_keyspace)

    sync_table(User)
    sync_table(Post)
    sync_table(Channel)
    sync_table(Project)

    # User related tables
    sync_table(UserTimeLine)
    sync_table(UserFollower)
    sync_table(UserFollowing)
    sync_table(UserPost)
    sync_table(UserProject)

    # Post related Tables
    sync_table(PostComment)
    sync_table(PostFollower)
    sync_table(PostLike)

    # Channel Related Tables
    sync_table(ChannelFollower)
    sync_table(ChannelTimeLine)

    # Project Related
    sync_table(ProjectFollower)
    sync_table(ProjectTimeLine)


def test_insert():
    from datetime import datetime as dt

    User.create(id=1, nick='bcambel', created_at=dt.utcnow(),
                extended={'test': "test"})

    Post.create(orig_id=1, text="Testing")


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent("""Screen6"""))
    parser.add_argument('hosts', )
    parser.add_argument('keyspace')

    return parser.parse_args()


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}

    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

# Usage example

if __name__ == '__main__':

    args = parse_args()
    from connection import setup, connect

    connect(*setup(args.hosts, args.keyspace))
    from hierachy import *

    if query_yes_no('Are you sure to sync ?', default='no'):
        create(args.keyspace)
        print "Done...."
    else:
        print "No is also a good thing. Bye!"