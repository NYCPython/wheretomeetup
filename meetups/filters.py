# Copyright (c) 2012, The NYC Python Meetup
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

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
