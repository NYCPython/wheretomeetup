from urllib import urlencode

from . import meetup
from .models import *

ORGANIZER_ROLES = set(['Organizer', 'Co-Organizer'])


def sync_user(member_id, maximum_staleness=3600):
    """Synchronize a user between the Meetup API and MongoDB. Typically called
    after a user login. In addition to creating or updating the `user` document,
    also synchronizes groups the user is associated with, and sets the `organizer_of`
    field in the `user` document with ``_id`` references that the user is an
    oragnizer of.

    Returns the populated and saved :class:`~meetups.models.User` object.
    """
    user = User(_id=member_id)
    user.load()
    user.refresh_if_needed(maximum_staleness)
    user.loc = (user.lon, user.lat)
    delattr(user, 'lon')
    delattr(user, 'lat')

    member_of = []
    organizer_of = []

    query = dict(member_id=user._id, fields='self', page=200, offset=0)
    while True:
        response = meetup.get('/2/groups/?%s' % urlencode(query))
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
        response = meetup.get('/2/venues/?%s' % urlencode(query),
            headers={'Accept-Charset': 'utf-8'})
        meta, results = response.data['meta'], response.data['results']

        for venue in results:
            venue_id = venue.pop('id')
            seen_venues.add(venue_id)

            location = venue.pop('lon'), venue.pop('lat')

            Venue(_id=venue_id, loc=location, **venue).save()

        if not bool(meta['next']):
            break
        query['offset'] += 1

    more_venues = []
    all_upcoming = 'upcoming,proposed,suggested'
    query = dict(group_id=group_ids, status=all_upcoming, page=200, offset=0)
    while True:
        response = meetup.get('/2/events/?%s' % urlencode(query),
            headers={'Accept-Charset': 'utf-8'})
        meta, results = response.data['meta'], response.data['results']

        for event in results:
            event_id = int(event.pop('id'))

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
