from flask import url_for, redirect


def load_user(user_id):
    from statuspage.models import User
    user = User.query.filter_by(id=user_id).first()
    return user


def unauthorized():
    return redirect(url_for('oauth.logout'))
