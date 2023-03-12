from django.core.checks import register
from django.template.defaulttags import URLNode
from django.urls import NoReverseMatch
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin

from django_robust.constants import RobustWarning
from django_robust.utils import get_subclasses_for_apps, template_exists, get_file_loc, walk


@register
def check_templates_exist(app_configs, **kwargs):
    for template_sub in get_subclasses_for_apps(TemplateResponseMixin, app_configs):
        template_name = template_sub.template_name
        if template_name is not None and not template_exists(template_name):
            yield RobustWarning.TemplateDoesNotExist(
                template_name=template_name,
                template_sub=template_sub,
                template_loc=get_file_loc(template_sub),
                obj=template_sub,
            )

@register
def check_view_success_url(app_configs, **kwargs):
    for form_sub in get_subclasses_for_apps(FormMixin, app_configs):
        success_url = form_sub.success_url
        if success_url is not None:
            try:
                str(success_url)
            except NoReverseMatch:
                yield RobustWarning.InvalidSuccessUrl(
                    success_url=success_url,
                    form_sub=form_sub,
                    form_loc=get_file_loc(form_sub),
                    obj=form_sub,
                )


def check_url_reverses(template_nodelist):
    for node in walk(*template_nodelist):
        if isinstance(node, URLNode):
            node.view_name
    pass  # look into