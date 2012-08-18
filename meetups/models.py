from datetime import datetime

from flask import session
from flask.ext.login import LoginManager, UserMixin, AnonymousUser

from meetups import meetup, mongo

login_manager = LoginManager()

@login_manager.user_loader
def load_user(id):
    user = User(_id=id)
    if user.load():
        return user
    return None

class Model(object):
    """Base class for data models. Supports three modes of operation:

    1. :meth:`load` to retrieve (cached) data from MongoDB
    2. :meth:`refresh` to retrieve data from the Meetup API
    3. :meth:`save` to save data back to MongoDB

    Subclasses should override the :attr:`api_endpoint`, :attr:`collection`,
    and :attr:`api_identifer` class-level attributes with appropriate values.
    Subclasses should have a field (or property)

    Subclasses may override :attr:`dont_save_fields` with a squence of
    field names that should not be saved to MongoDB.

    Subclasses may override :attr:`field_mapping` which maps field names
    from the Meetup API to names that will be used on object attributes
    and stored in MongoDB.
    """

    api_endpoint = None
    api_identifier = None
    collection = None
    field_mapping = {}
    dont_save_fields = []

    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def load(self):
        """Return ``True`` if the document was found, or ``False`` otherwise.
        """
        if not hasattr(self, '_id'):
            raise TypeError('Model subclasses must define an _id attribute')
        if self.collection is None:
            raise TypeError('Model subclasses must set a collection attribute')

        doc = mongo.db[self.collection].find_one(self._id) or {}
        for k, v in doc.iteritems():
            setattr(self, k, v)

        return bool(doc)

    def refresh(self):
        if self.api_endpoint is None:
            raise TypeError('Model subclasses must set an api_endpoint attribute')
        if self.api_identifier is None:
            raise TypeError('Model subclasses must set an api_identifier attribute')

        url = self.api_endpoint % vars(self)
        data = getattr(meetup.get(url), 'data', {})
        for k, v in data.iteritems():
            k = self.field_mapping.get(k, k)
            setattr(self, k, v)

    def refresh_if_needed(self, maximum_staleness):
        """Check the :attr:`modified` timestamp, and call :meth:`refresh` if
        it is older than the `maximum_staleness` (in seconds). Return ``True``
        if :meth:`refresh` was called, and ``False`` otherwise.
        """
        created = getattr(self, 'created', datetime(1970, 1, 1, 0, 0, 0))
        staleness = datetime.utcnow() - created
        if staleness.total_seconds() > maximum_staleness:
            self.refresh()
            return True
        return False

    def save(self):
        if not hasattr(self, '_id'):
            raise TypeError('Model subclasses must define an _id attribute')
        if self.collection is None:
            raise TypeError('Model subclasses must set a collection attribute')

        doc = {}
        for k, v in vars(self).iteritems():
            if k in ('api_endpoint', 'api_identifier', 'collection', 'dont_save_fields'):
                continue
            if k in self.dont_save_fields:
                continue
            doc[k] = v

        now = datetime.utcnow()
        if 'created' not in doc:
            doc['created'] = now
        doc['modified'] = now

        mongo.db[self.collection].update({'_id': doc['_id']}, doc, upsert=True)


class User(Model, UserMixin):
    api_endpoint = '/2/member/%(_id)s'
    api_identifier = '_id'
    field_mapping = {
        'id': '_id'
    }
    collection = 'users'

    def get_id(self):
        """Make this model compatible with expectations of Flask-Login.
        """
        return self._id

class Guest(AnonymousUser):
    # define name to be compatible with :class:`User`
    name = 'Guest'
login_manager.anonymous_user = Guest
