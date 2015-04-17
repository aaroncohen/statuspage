import os
from flask import Flask, send_from_directory
from flask.ext.googlelogin import GoogleLogin
from flask.ext.login import LoginManager
from flask.ext.appconfig import AppConfig

from statuspage import database
from statuspage.user_manager import load_user, unauthorized


def create_app(configfile=None):
    new_app = Flask(__name__)
    AppConfig(new_app, configfile)
    return new_app

# Loads settings from default_config.py, then from a .cfg file specified in STATUSPAGE_CONFIG env var,
# then from any environment variables prefixed with STATUSPAGE_
app = create_app()

app.secret_key = os.urandom(24)

database.init_db(app)

login_manager = LoginManager()
login_manager.user_callback = load_user
# login_manager.unauthorized_callback = unauthorized
login_manager.init_app(app)
login_manager.login_view = "oauth.login"
google_login = GoogleLogin(app, login_manager)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def register_blueprints(app):
    # Prevents circular imports
    from blueprints.page import statuspage
    from blueprints.admin import admin
    from blueprints.oauth import oauth

    app.register_blueprint(statuspage)
    app.register_blueprint(admin)
    app.register_blueprint(oauth)


register_blueprints(app)


if __name__ == '__main__':
    app.run()
