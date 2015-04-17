import urlparse
from flask import Blueprint, redirect, url_for, request, render_template
from flask.ext.login import login_user, logout_user

from statuspage import google_login, app
from statuspage.database import db
from statuspage.models import User

oauth = Blueprint('oauth', __name__, url_prefix='', template_folder='templates')

@google_login.oauth2callback
def create_or_update_user(token, userinfo, **params):
    user = User.query.filter_by(google_id=userinfo.get('id', None)).first()
    if not user:
        user = User()
        user.google_id = userinfo.get('id', None)

    user.name = userinfo.get('name', "NO NAME")
    user.picture = userinfo.get('picture', None)
    user.email = userinfo.get('email', None)

    db.session.add(user)
    db.session.commit()

    login_user(user)

    next_url = params.get('next', '')
    if next_url and next_url.startswith(request.host_url) and not next_url.startswith(request.base_url):
        return redirect(next_url)
    else:
        return redirect(url_for('admin.pages'))


def login():
    next_page = request.values.get('next', '')
    if next_page:
        next_url = urlparse.urljoin(request.host_url, next_page)
    else:
        next_url = ''
    return render_template('login.html',
                           login_url=google_login.login_url(
                               scopes=app.config.get('GOOGLE_LOGIN_CLIENT_SCOPES', ''),
                               hd=app.config.get('RESTRICT_LOGIN_DOMAIN', ''),
                               params=dict(next=next_url)
                           )
    )


def logout():
    logout_user()
    return redirect(url_for('oauth.login'))

oauth.add_url_rule('/oauth2callback', view_func=create_or_update_user)
oauth.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
oauth.add_url_rule('/logout', view_func=logout)
