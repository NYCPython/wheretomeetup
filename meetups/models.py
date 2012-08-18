from flask import session

from flask.ext.login import LoginManager, UserMixin, AnonymousUser

login_manager = LoginManager()


@login_manager.user_loader
def load_user(id):
    member_id = session.get('meetup_member_id')
    if member_id == id:
        return User(session['meetup_member_id'], session['user_name'])
    return None


class User(UserMixin):
    class Meta:
        collection = 'users'

    def __init__(self, meetup_member_id, user_name):
        self.id = self.meetup_member_id = meetup_member_id
        self.user_name = user_name

class Guest(AnonymousUser):
    user_name = 'Guest'
login_manager.anonymous_user = Guest
