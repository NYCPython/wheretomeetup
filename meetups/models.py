from flask.ext.login import LoginManager, UserMixin

login_manager = LoginManager()


@login_manager.user_loader
def load_user(id):
    return User.get(id)


class User(UserMixin):
    class Meta:
        collection = 'users'
