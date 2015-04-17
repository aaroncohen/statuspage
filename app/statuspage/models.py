from datetime import datetime
from collections import Counter

from flask.ext.login import UserMixin
from statuspage.database import db
from statuspage import app


class Serializer(object):
    __public__ = []

    def to_serializable_dict(self):
        dict = {}
        for public_key in self.__public__:
            value = getattr(self, public_key)
            if value:
                dict[public_key] = value
        return dict


class User(UserMixin, db.Model, Serializer):
    __tablename__ = 'users'
    __public__ = ['id', 'name', 'google_id', 'picture', 'email', 'created_at', 'modified_at']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    google_id = db.Column(db.String(255), unique=True)
    picture = db.Column(db.String(4096), nullable=True)
    email = db.Column(db.String(255), unique=True)
    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def __init__(self, oauth_response=None):
        if oauth_response is not None:
            self.update_from_oauth_data(oauth_response)
        self.created_at = self.modified_at = datetime.utcnow()

    def update_from_oauth_data(self, oauth_response):
        self.name = oauth_response.get('name', 'NO NAME')
        self.google_id = oauth_response.get('id', 'NO ID')
        self.picture = oauth_response.get('picture', 'NO PICTURE')
        self.email = oauth_response.get('email', 'NO EMAIL')

    @property
    def is_admin(self):
        admin_ids = app.config.get('ADMIN_GOOGLE_IDS')
        return (self.email and self.email in admin_ids) or 'all' in admin_ids

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return "<User %s - %s>" % (self.email, self.name)


class Page(db.Model, Serializer):
    __tablename__ = "pages"
    __public__ = ['id', 'name', 'slug', 'hero_image_url', 'created_at', 'updated_at']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    slug = db.Column(db.String(255), index=True, unique=True)
    hero_image_url = db.Column(db.String(4096), nullable=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    # backref - components
    # backref - incidents

    @property
    def status(self):
        counts = Counter([component.status for component in self.components])
        if counts['major_outage'] > 1:
            return 'major_outage'
        elif counts['major_outage'] or counts['partial_outage']:
            return 'partial_outage'
        elif counts['degraded_performance']:
            return 'degraded_performance'
        else:
            return 'all_services_operational'


class Component(db.Model, Serializer):
    __tablename__ = "components"
    __public__ = ['id', 'name', 'description', 'position', 'status', 'updated_at', 'page_id']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(4096))
    position = db.Column(db.Integer)
    status = db.Column(db.Enum('operational',
                               'degraded_performance',
                               'partial_outage',
                               'major_outage',
                               name='comp_status_types'))
    updated_at = db.Column(db.DateTime)

    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'))
    page = db.relationship('Page',
                           backref=db.backref('components', cascade="all,delete-orphan"))


class Incident(db.Model, Serializer):
    __tablename__ = "incidents"
    __public__ = ['id', 'name', 'impact', 'created_at', 'updated_at', 'resolved_at', 'scheduled_for', 'scheduled_until',
                  'page_id', 'component_problem', 'component_id']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    @property
    def status(self):
        last_update = self.last_update
        if last_update:
            return last_update.status
        else:
            return 'investigating'

    @property
    def last_update(self):
        return Update.query.filter_by(incident_id=self.id).order_by('-id').first()

    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    resolved_at = db.Column(db.DateTime, nullable=True)
    scheduled_for = db.Column(db.DateTime, nullable=True)
    scheduled_until = db.Column(db.DateTime, nullable=True)

    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'))
    page = db.relationship('Page',
                           backref=db.backref('incidents', cascade="all,delete-orphan"))


    # backref - updates


class Update(db.Model, Serializer):
    __tablename__ = "updates"
    __public__ = [id, 'body', 'created_at', 'updated_at', 'display_at', 'incident_id', 'status', 'is_postmortem']
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.UnicodeText)

    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    display_at = db.Column(db.DateTime, nullable=True)

    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'))
    incident = db.relationship('Incident',
                               foreign_keys='Update.incident_id',
                               backref=db.backref('updates', cascade="all,delete-orphan"))

    # status - investigating, identified, monitoring, resolved (if realtime)
    #            scheduled, in_progress, verifying, completed (if scheduled)
    status = db.Column(db.Enum('investigating',
                               'identified',
                               'monitoring',
                               'resolved',
                               'scheduled',
                               'in_progress',
                               'verifying',
                               'completed',
                               name='update_status_types'))

    is_postmortem = db.Column(db.Boolean, default=False)
