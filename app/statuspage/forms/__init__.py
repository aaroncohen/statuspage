from flask.ext.wtf import Form
from statuspage.database import db
from wtforms_alchemy import model_form_factory
# The variable db here is a SQLAlchemy object instance from
# Flask-SQLAlchemy package


BaseModelForm = model_form_factory(Form)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(cls):
        return db.session
