from urllib import urlencode

from . import meetup
from .models import *

ORGANIZER_ROLES = set(['Organizer', 'Co-Organizer'])


def _get_list(cls, query, sort):
    """Generate instances of `cls` that match the given query.
    """
    docs = mongo.db[cls.collection].find(query)
    if sort:
        docs.sort(sort)
    return (cls(**doc) for doc in docs)


def get_users_venues(user_id):
    """Fetch a list of all venues that have been claimed by a
    :class:`~meetups.models.User`.

    Returns a list of :class:`~meetups.models.Venue` objects.
    """
    return _get_list(Venue, {'user_id': user_id}, 'name')


def get_unclaimed_venues():
    """Fetch a list of all venues that have yet to be claimed.

    Returns a list of :class:`~meetups.models.Venue` objects.
    """
    return _get_list(Venue, {'claimed': False}, 'name')


def get_groups(query, sort=None):
    """Return a list of :class:`~meetups.models.Group` objects that
    match the given query.
    """
    return _get_list(Group, query, sort)


def get_events(query, sort=None):
    """Return a list of :class:`~meetups.models.Event` objects that
    match the given query.
    """
    return _get_list(Event, query, sort)


def get_venues(query, sort=None):
    """Return a list of :class:`~meetups.models.Venue` objects that
    match the given query.
    """
    return _get_list(Venue, query, sort)


def _meetup_get(endpoint):
    """Make a GET request to the Meetup API and set common headers
    and options.
    """
    return meetup.get(endpoint, headers={'Accept-Charset': 'utf-8'})


def sync_user(member_id, maximum_staleness=3600):
    """Synchronize a user between the Meetup API and MongoDB. Typically called
    after a user login. In addition to creating or updating the `user` document,
    also synchronizes groups the user is associated with, and sets the `organizer_of`
    field in the `user` document with ``_id`` references that the user is an
    oragnizer of.

    Returns the populated and saved :class:`~meetups.models.User` object.
    """
    user = User(_id=member_id).load()
    user.refresh_if_needed(maximum_staleness)
    user.loc = (user.lon, user.lat)
    delattr(user, 'lon')
    delattr(user, 'lat')

    member_of = []
    organizer_of = []

    query = dict(member_id=user._id, fields='self', page=200, offset=0)
    while True:
        response = _meetup_get('/2/groups/?%s' % urlencode(query))
        meta, results = response.data['meta'], response.data['results']

        for group in results:
            group_id = group.pop('id')

            self = group.pop('self', {})
            if self.get('role', None) in ORGANIZER_ROLES:
                organizer_of.append(group_id)
            member_of.append(group_id)

            Group(_id=group_id, **group).save()

        if not bool(meta['next']):
            break
        query['offset'] += 1

    user.member_of = member_of
    user.organizer_of = organizer_of
    user.save()

    seen_venues = set()
    group_ids = ','.join(str(x) for x in member_of)
    query = dict(group_id=group_ids, fields='taglist', page=200, offset=0)
    while True:
        response = _meetup_get('/2/venues/?%s' % urlencode(query))
        meta, results = response.data['meta'], response.data['results']

        for venue in results:
            venue_id = venue.pop('id')
            seen_venues.add(venue_id)

            location = venue.pop('lon'), venue.pop('lat')

            Venue(_id=venue_id, loc=location, **venue).save()

        if not bool(meta['next']):
            break
        query['offset'] += 1

    # Set defaults on any newly created venues
    mongo.db[Venue.collection].update({'claimed': {'$exists': False}},
        {'$set': {'claimed': False}}, multi=True)
    mongo.db[Venue.collection].update({'deleted': {'$exists': False}},
        {'$set': {'deleted': False}}, multi=True)

    more_venues = []
    all_upcoming = 'upcoming,proposed,suggested'
    query = dict(group_id=group_ids, status=all_upcoming, fields='rsvp_limit', page=200, offset=0)
    while True:
        response = _meetup_get('/2/events/?%s' % urlencode(query))
        meta, results = response.data['meta'], response.data['results']
        
        for event in results:
            event_id = event.pop('id')

            venue = event.pop('venue', None)
            if venue:
                venue_id = venue.pop('id')
                if venue_id not in seen_venues:
                    more_venues.append(venue_id)

            group = event.pop('group')
            event['group_id'] = group.pop('id')

            Event(_id=event_id, **event).save()

        if not bool(meta['next']):
            break
        query['offset'] += 1

    # TODO:
    # for venue in more_venues:
    #     get_venue()

    return user
