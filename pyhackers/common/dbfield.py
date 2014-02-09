import base64
from datetime import datetime as dt, timedelta
import logging
import pickle
from sqlalchemy.types import TypeDecorator, CHAR, String, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses Postgresql's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                return "%.32x" % value # hexstring

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class Choice(TypeDecorator):
    impl = String

    def __init__(self, choices=None, **kw):
        if choices is None:
            choices = {}
        self.choices = dict(choices)
        super(Choice, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.iteritems() if v == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]


class EpochType(TypeDecorator):
    impl = Integer

    epoch = dt.date(dt(1970, 1, 1))

    def process_bind_param(self, value, dialect):
        return (value - self.epoch).days

    def process_result_value(self, value, dialect):
        return self.epoch + timedelta(days=value)


class GzippedDictField(TypeDecorator):
    """
    Slightly different from a JSONField in the sense that the default
    value is a dictionary.
    """
    impl = Text

    def process_result_value(self, value, dialect):
        if isinstance(value, basestring) and value:
            try:
                value = pickle.loads(base64.b64decode(value).decode('zlib'))
            except Exception, e:
                logging.exception(e)
                return {}
        elif not value:
            return {}
        return value

        pass

    def process_bind_param(self, value, dialect):
        if value is None:
            return
        return base64.b64encode(pickle.dumps(value).encode('zlib'))