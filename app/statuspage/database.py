from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy

db = None
migrate = None


def init_db(app):
    global db, migrate
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    from models import Component, Incident, Page, User, Update
    db.create_all()
    db.session.commit()
