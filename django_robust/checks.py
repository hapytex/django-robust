from django.core.checks import register
from django.forms import ModelForm
from django.template.defaulttags import URLNode
from django.urls import NoReverseMatch
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin

from django_robust.constants import RobustWarning
from django_robust.walk import walk
from django_robust.utils import template_exists, get_file_loc, AppConfigFilter, any_override


@RobustWarning.TemplateDoesNotExist.register_check
def check_templates_exist(app_configs, trigger, **kwargs):
    for template_sub in app_configs.get_subclasses_for_apps(TemplateResponseMixin):
        template_name = template_sub.template_name
        if template_name is not None and not template_exists(template_name):
            yield trigger(
                template_name=template_name,
                template_sub=template_sub,
                template_loc=get_file_loc(template_sub),
                obj=template_sub,
            )

@RobustWarning.InvalidSuccessUrl.register_check
def check_view_success_url(app_configs, trigger, **kwargs):
    for form_sub in app_configs.get_subclasses_for_apps(FormMixin):
        success_url = form_sub.success_url
        if success_url is not None:
            try:
                str(success_url)  # TODO: missing parameters?
            except NoReverseMatch:
                yield trigger(
                    success_url=success_url,
                    form_sub=form_sub,
                    form_loc=get_file_loc(form_sub),
                    obj=form_sub,
                )


@RobustWarning.NoQuerySetConfigured.register_check
def check_view_queryset(app_configs: AppConfigFilter, trigger, **kwargs):
    for klass, overrides in [
        (SingleObjectMixin, ('model', 'queryset', 'get_queryset', 'get_object')),
        (MultipleObjectMixin, ('model', 'queryset', 'get_queryset'))
    ]:
        for sub in app_configs.get_subclasses_for_apps(klass):
            if not any_override(klass, sub, *overrides):
                yield trigger(
                    sub=sub
                )

@RobustWarning.ModelFormWithoutMeta.register_check
def check_modelform_meta(app_configs: AppConfigFilter, trigger, **kwargs):
    for modelform in app_configs.get_subclasses_for_apps(ModelForm):
        if not hasattr(modelform, 'Meta'):
            trigger(
                modelform=modelform
            )


def check_url_reverses(template_nodelist):
    for node in walk(*template_nodelist):
        if isinstance(node, URLNode):
            node.view_name
    pass  # look into