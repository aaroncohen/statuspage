from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask.ext.login import current_user, login_required
from flask.views import MethodView
from statuspage.database import db
from statuspage.forms.page import PageForm
from statuspage.models import Page, Component, Incident, Update

admin = Blueprint('admin', __name__, template_folder='templates')


@admin.before_request
def before_request():
    if not current_user or current_user.is_anonymous() or not current_user.is_admin:
        return redirect(url_for('oauth.login'))


class PageAdminView(MethodView):
    @login_required
    def get(self):
        pages = Page.query.all()
        return render_template('admin/pages.html', pages=pages, current_user=current_user)


class PageAdminDetailView(MethodView):
    @login_required
    def get(self, page_slug):
        page = Page.query.filter_by(slug=page_slug).first_or_404()
        return render_template('admin/components.html', page=page, current_user=current_user)


class PageEditView(MethodView):
    def get_context(self, page_slug=None):
        if page_slug:
            page = Page.query.filter_by(slug=page_slug).first_or_404()

            if request.method == 'POST':
                form = PageForm(request.form, obj=page)
            else:
                form = PageForm(obj=page)
        else:
            page = Page()
            form = PageForm(request.form)

        context = {
            "current_user": current_user,
            "page": page,
            "form": form,
            "create": page_slug is None
        }
        return context

    @login_required
    def get(self, page_slug):
        context = self.get_context(page_slug)
        return render_template('admin/customize.html', **context)

    @login_required
    def post(self, page_slug):
        context = self.get_context(page_slug)
        form = context.get('form')
        if form.validate_on_submit():
            page = context.get('page')
            form.populate_obj(page)

            now = datetime.now()
            if context.get('create', False):
                page.created_at = now
            page.updated_at = now

            db.session.add(page)
            db.session.commit()

            if context.get('create', True):
                return redirect(url_for('admin.pages'))
            else:
                return redirect(url_for('admin.page.dashboard', page_slug=page.slug))
        return render_template('admin/customize.html', **context)


class PageDelete(MethodView):
    @login_required
    def post(self, page_slug):
        page = Page.query.filter_by(slug=page_slug).first_or_404()

        db.session.delete(page)
        db.session.commit()

        return redirect(url_for('admin.pages'))


class PageDashboard(MethodView):
    @login_required
    def get(self, page_slug):
        page = Page.query.filter_by(slug=page_slug).first_or_404()

        return render_template('admin/dashboard.html', page=page)


class PageComponents(MethodView):
    @login_required
    def get(self, page_slug):
        page = Page.query.filter_by(slug=page_slug).first_or_404()

        return render_template('admin/components.html', page=page)


class PageComponent(MethodView):
    @login_required
    def get(self, page_slug, component_id):
        # page = Page.query.filter_by(slug=page_slug).first_or_404()
        component = Component.query.get_or_404(component_id)
        return render_template('admin/partials/components_item.html', component=component)


class PageComponentsOrder(MethodView):
    @login_required
    def post(self, page_slug):
        order = request.values.getlist('item[]')

        components_to_update = []
        for index, item in enumerate(order):
            component = Component.query.get(item)
            if component:
                component.position = index
                components_to_update.append(component)

        db.session.add_all(components_to_update)
        db.session.commit()

        return jsonify({
            'action': 'reorder',
            'components': [component.to_serializable_dict() for component in components_to_update]
        })


class PageComponentsCreate(MethodView):
    @login_required
    def post(self, page_slug):
        page = Page.query.filter_by(slug=page_slug).first_or_404()
        new_component = Component(name=request.form.get('name', 'Unknown Name'),
                                  description=request.form.get('description', ''),
                                  position=len(page.components),
                                  status="operational",
                                  updated_at=datetime.now(),
                                  page=page)

        db.session.add(new_component)
        db.session.commit()

        return render_template('admin/partials/components_item.html', component=new_component)


class PageComponentsEdit(MethodView):
    @login_required
    def get(self, page_slug, component_id):
        # page = Page.query.filter_by(slug=page_slug).first_or_404()
        component = Component.query.get_or_404(component_id)
        return render_template('admin/partials/components_edit_item.html', component=component)

    @login_required
    def post(self, page_slug, component_id):
        # page = Page.query.filter_by(slug=page_slug).first_or_404()
        component = Component.query.get_or_404(component_id)

        component.name = request.form.get('name', 'Unknown Name')
        component.description = request.form.get('description', '')

        db.session.add(component)
        db.session.commit()

        return render_template('admin/partials/components_item.html', component=component)


class PageComponentsStatus(MethodView):
    @login_required
    def post(self, page_slug, component_id):
        # page = Page.query.filter_by(slug=page_slug).first_or_404()
        component = Component.query.get_or_404(component_id)

        component.status = request.form.get("component-status-radios-%s" % component_id, 'operational')

        db.session.add(component)
        db.session.commit()

        return jsonify({'action': 'set_status', 'component_id': component.id, 'value': component.status})


class PageComponentsDelete(MethodView):
    @login_required
    def post(self, page_slug, component_id):
        component = Component.query.get_or_404(component_id)
        db.session.delete(component)
        db.session.commit()

        return jsonify({'action': 'deleted', 'component_id': component.id})


class PageIncidentsCreate(MethodView):
    @login_required
    def post(self, page_slug):
        page = Page.query.filter_by(slug=page_slug).first_or_404()
        new_incident = Incident(name=request.form.get('name', 'Unknown Problem'),
                                page=page)

        new_update = Update(body=request.form.get('message', "We're looking into it."),
                            status=request.form.get('status', "investigating"),
                            incident=new_incident)

        now = datetime.now()
        new_incident.created_at = new_update.created_at = now
        new_incident.updated_at = new_update.updated_at = now

        if new_update.status == 'resolved':
            new_incident.resolved_at = now

        db.session.add(new_incident)
        db.session.add(new_update)
        db.session.commit()

        return redirect(url_for('admin.page.dashboard', page_slug=page_slug))


class PageIncidentsUpdate(MethodView):
    @login_required
    def post(self, page_slug, incident_id):
        incident = Incident.query.get_or_404(incident_id)

        new_update = Update(body=request.form.get('message', "We're looking into it."),
                            status=request.form.get('status', "investigating"),
                            incident=incident)

        now = datetime.now()
        new_update.created_at = now
        incident.updated_at = new_update.updated_at = now

        if new_update.status == 'resolved':
            incident.resolved_at = now

        db.session.add(incident)
        db.session.add(new_update)
        db.session.commit()

        return redirect(url_for('admin.page.dashboard', page_slug=page_slug))


class PageIncidentsDelete(MethodView):
    @login_required
    def post(self, page_slug, incident_id):
        incident = Incident.query.get_or_404(incident_id)

        db.session.delete(incident)
        db.session.commit()

        return redirect(url_for('admin.page.incidents', page_slug=page_slug))


# Register the urls

# Page Administration
admin.add_url_rule('/page/admin', view_func=PageAdminView.as_view('pages'))
admin.add_url_rule('/page/<page_slug>/admin', view_func=PageAdminDetailView.as_view('page_detail'))

admin.add_url_rule('/page/create', defaults={'page_slug': None}, view_func=PageEditView.as_view('page.create'))
admin.add_url_rule('/page/<page_slug>/admin/customize', view_func=PageEditView.as_view('page.customize'))
admin.add_url_rule('/page/<page_slug>/admin/delete', view_func=PageDelete.as_view('page.delete'))

# Page Dashboard
admin.add_url_rule('/page/<page_slug>/admin/dashboard', view_func=PageDashboard.as_view('page.dashboard'))

# Page Components
admin.add_url_rule('/page/<page_slug>/admin/components', view_func=PageComponents.as_view('page.components'))
admin.add_url_rule('/page/<page_slug>/admin/components/<component_id>',
                   view_func=PageComponent.as_view('page.component'))
admin.add_url_rule('/page/<page_slug>/admin/components/order',
                   view_func=PageComponentsOrder.as_view('page.components.order'))
admin.add_url_rule('/page/<page_slug>/admin/components/create',
                   view_func=PageComponentsCreate.as_view('page.components.create'))
admin.add_url_rule('/page/<page_slug>/admin/components/<component_id>/edit',
                   view_func=PageComponentsEdit.as_view('page.components.edit'))
admin.add_url_rule('/page/<page_slug>/admin/components/<component_id>/status',
                   view_func=PageComponentsStatus.as_view('page.components.status'))
admin.add_url_rule('/page/<page_slug>/admin/components/<component_id>/delete',
                   view_func=PageComponentsDelete.as_view('page.components.delete'))

# Page Incidents/Updates
admin.add_url_rule('/page/<page_slug>/admin/incidents/create',
                   view_func=PageIncidentsCreate.as_view('page.incidents.create'))
admin.add_url_rule('/page/<page_slug>/admin/incidents/<incident_id>/update',
                   view_func=PageIncidentsUpdate.as_view('page.incidents.update'))
admin.add_url_rule('/page/<page_slug>/admin/incidents/<incident_id>/delete',
                   view_func=PageIncidentsDelete.as_view('page.incidents.delete'))
