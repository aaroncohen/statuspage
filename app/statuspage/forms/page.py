from statuspage.models import Page
from statuspage.forms import ModelForm


class PageForm(ModelForm):
    class Meta:
        model = Page
        exclude = ['created_at', 'updated_at']
