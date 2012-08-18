from . import app, meetup, mongo
from flask import render_template, redirect, url_for, request, session, flash
from flask.ext.login import login_required, login_user, logout_user

from .logic import sync_user, get_unclaimed_venues
from .models import User, Group, Venue, Event, login_manager
from .forms import VenueClaimForm, RequestForSpaceForm


@app.route('/clear/')
def clear():
    session.clear()
    return redirect('/')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/have/')
def have():
    venues = get_unclaimed_venues()
    return render_template('have.html', venues=venues)


@app.route('/login/', methods=('GET', 'POST'))
def login():
    return meetup.authorize(callback=url_for('login_meetup_return'))


@app.route('/login/meetup/return/', methods=('GET',))
@meetup.authorized_handler
def login_meetup_return(oauth_response):
    session['meetup_token'] = (
        oauth_response['oauth_token'],
        oauth_response['oauth_token_secret']
    )
    session['member_id'] = oauth_response['member_id']
    return render_template('login.html')


@app.route('/login/sync/', methods=('GET',))
def login_sync():
    user = sync_user(session['member_id'])
    login_user(user, remember=True)
    return redirect(url_for('index'))


@app.route('/logout/')
def logout():
    session.pop('meetup_token', None)
    session.pop('meetup_member_id', None)
    logout_user()
    return redirect(url_for('.index'))


@app.route('/have/')
def have():
    return render_template('have.html')


@app.route('/need/')
@login_required
def need():
    user = User(_id=int(session['member_id']))
    user.load()
    groups = [Group(**doc) for doc in
              mongo.db.groups.find({'_id': {'$in': user.organizer_of}})]
    return render_template('need.html',
        user=user,
        groups=groups,
    )


@app.route('/need/group/<int:group_id>/')
@login_required
def need_event(group_id):
    user = User(_id=int(session['member_id']))
    user.load()
    group = Group(_id=group_id)
    group.load()
    events = [Event(**doc) for doc in
              mongo.db.events.find({'group_id': group._id})]
    return render_template('need.html',
        user=user,
        group=group,
        events=events,
    )

@app.route('/need/group/<int:group_id>/event/<int:event_id>/')
@login_required
def need_venue(group_id, event_id):
    user = User(_id=int(session['member_id']))
    user.load()
    group = Group(_id=group_id)
    group.load()
    event = Event(_id=event_id)
    event.load()
    all_venues = [Venue(**doc) for doc in
                  mongo.db.venues.find({
                      'loc': {'$near': user.loc},
                      'claimed': True,
                      'deleted': False,
                  })]
    return render_template('need.html',
        user=user,
        group=group,
        event=event,
        all_venues=all_venues,
    )

@app.route('/need/group/<int:group_id>/event/<int:event_id>/request/', methods=('POST',))
@login_required
def need_request(group_id, event_id):
    venue_ids = request.form.getlist('venue_id', type=int)
    if not venue_ids:
        flash(u'You need to pick at least one venue!', 'warning')
        return redirect('need_venue', group_id=group_id, event_id=event_id)

    user = User(_id=int(session['member_id']))
    user.load()
    group = Group(_id=group_id)
    group.load()
    event = Event(_id=event_id)
    event.load()
    all_venues = [Venue(**doc) for doc in
                  mongo.db.venues.find({
                      'loc': {'$near': user.loc},
                      'claimed': True,
                      'deleted': False,
                  })]
    picked_venues = []
    venue_ids = set(venue_ids)
    for venue in all_venues:
        if venue._id in venue_ids:
            picked_venues.append(venue)
    picked_venue_names = [v.name for v in picked_venues]

    request_form = RequestForSpaceForm()

    return render_template('need.html',
        user=user,
        group=group,
        event=event,
        all_venues=all_venues,
        picked_venues=picked_venues,
        picked_venue_names=picked_venue_names,
        request_form=request_form,
    )


@app.route('/need/group/<int:group_id>/event/<int:event_id>/request/submit/', methods=('POST',))
@login_required
def need_request_submit(group_id, event_id):
    print "SEND AN EMAIL!"
    return 'SEND AN EMAIL!'


@app.route('/venue/<int:_id>/claim/', methods=('GET', 'POST'))
def venue_claim(_id):
    venue = Venue(_id=_id)
    venue.load()

    user = User(_id=int(session['member_id']))
    user.load()

    # If the user has not email or phone number and the venue does, place
    # them on the user for the purpose for prepopulating the form.
    if not getattr(user, 'email', None) and getattr(venue, 'email', None):
        user.email = venue.email
    if not getattr(user, 'phone', None) and getattr(venue, 'phone', None):
        user.phone = venue.phone

    form = VenueClaimForm(request.form, obj=user)
    if request.method == 'POST' and form.validate():
        venue.claim(name=form.name.data, email=form.email.data,
            phone=form.phone.data)
        flash('Thank you for claiming %s' % venue.name, 'success')
        return redirect(url_for('index'))

    return render_template('venue/claim.html', venue=venue, form=form)


@meetup.tokengetter
def get_meetup_token():
    return session.get('meetup_token')


@login_manager.unauthorized_handler
def login_prompt():
    # TODO: eventually, prompt the user so they are not surprised
    # that we are redirecting them to Meetup to log in
    return redirect(url_for('login'))
