import re
from datetime import datetime

from pytz import timezone, utc

from . import app
from .models import Event

# Match any 0 that is followed by another digit and
# that is not preceded by a :, and which is followed
# by a space or a colon, but not if that is followed
# by "am", "pm", "AM", or "PM"
zeroes = re.compile(r'(?<!:)0(\d[ :])(?!am|pm|AM|PM)')


@app.template_filter()
def event_date(event, fmt='%a, %b %d %Y %I:%M %p', strip_zeroes=True):
    """Format an :class:`~meetups.models.Event` date for display.
    """
    if not isinstance(event, Event) or not hasattr(event, 'time'):
        return u''

    # event.time is milliseconds since epoch, UTC
    timestamp = event.time / 1000
    when = datetime.utcfromtimestamp(timestamp)

    # TODO: convert to viewing user's timezone
    when = when.replace(tzinfo=utc).astimezone(timezone('US/Eastern'))
    formatted = when.strftime(fmt)

    if strip_zeroes:
        formatted = zeroes.sub(r'\1', formatted)

    return formatted


@app.template_filter()
def event_venue(event, prefix=''):
    """Format an :class:`~meetups.models.Event` venue for display.
    """
    if not isinstance(event, Event) or not hasattr(event, 'venue'):
        return u''

    return ('%s %s' % (prefix, event.venue['name'])).strip()
