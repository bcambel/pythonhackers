import logging
from pyhackers.model.cassandra.hierachy import ChannelFollower, Channel as CsChannel
from pyhackers.model.channel import Channel


def follow_channel(channel_id, current_user):
    ChannelFollower.create(channel_id=channel_id, user_id=current_user.id)


def load_channel(slugish):
    slug = slugish.lower()

    logging.info(u"Loading channel {}".format(slug))
    ch = Channel.query.filter_by(slug=slug).first()
    logging.info(ch)

    cassa_channel = CsChannel.filter(slug=slug).first()

    logging.info(cassa_channel)

    if cassa_channel is None and ch is not None:
        CsChannel.create(id=ch.id, slug=ch.slug, name=ch.name)


def get_channel_list():
    channels = [channel for channel in Channel.query.all()]
    return channels