import datetime
from flask import Blueprint, render_template
from flask.views import MethodView
from sqlalchemy import desc
from statuspage.models import Page, Incident


statuspage = Blueprint('statuspage', __name__, template_folder='templates')


class StatusPageView(MethodView):
    def get(self, page_slug):
        page = Page.query.filter_by(slug=page_slug).first_or_404()

        today = datetime.datetime.today()
        fifteen_days_ago = today - datetime.timedelta(days=15)
        past_incidents = Incident.query.\
            filter(Incident.page_id == page.id and Incident.created_at > fifteen_days_ago).\
            order_by(desc(Incident.created_at)).all()

        past_dates = [
                        {
                            'date': today - datetime.timedelta(days=x),
                            'incidents': [incident for incident in past_incidents
                                          if incident.created_at.date() == (today - datetime.timedelta(days=x)).date()]
                        } for x in range(0, 15)
        ]

        return render_template('statuspage.html', page=page, past_dates=past_dates)


class StatusEmbedView(MethodView):
    def get(self, page_slug):
        page = Page.query.filter_by(slug=page_slug).first_or_404()

        return render_template('mini_embed.html', page=page)


# Register the urls
statuspage.add_url_rule('/page/<page_slug>', view_func=StatusPageView.as_view('statuspage'))
statuspage.add_url_rule('/page/<page_slug>/embed', view_func=StatusEmbedView.as_view('statuspage.embed'))
