import inspect
from operator import attrgetter
from typing import Iterable, TypeVar

from django.apps import apps
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.views.generic.base import TemplateResponseMixin


T = TypeVar('T')


def get_app_configs(app_configs=None):
    if app_configs is None:
        return apps.get_app_configs()
    return app_configs

def walk(item : T, *items: T, children_field=None) -> Iterable[T]:
    # we use a stack to avoid making recursive calls which are expensive and
    # can run out of call stack.
    if isinstance(children_field, str):
        children_field = attrgetter(children_field)
    elif children_field is None:
        children_field = iter  # default: just iterate over the "parent"
    assert callable(children_field)
    stack = [*reversed(items), item]
    while stack:
        cur = stack.pop()
        to_add = yield cur
        try:
            children = children_field(item)
        except (TypeError, AttributeError, ValueError):
            pass
        else:
            if children:
                stack.extend(children)
        if to_add is not None:
            # the walker can provide feedback to add to the stack
            # these will be evaluated first.
            stack.extend(to_add)



def get_subclasses(root_class: type[T]) -> Iterable[type[T]]:
    yield root_class
    seen = gen = {root_class}
    while gen:
        next_gen = {sub for klass in gen for sub in klass.__subclasses__() if sub not in seen}
        yield from next_gen
        seen.update(next_gen)
        gen = next_gen


def get_subclasses_for_apps(root_class: type, app_configs=None):
    app_configs = get_app_configs(app_configs)
    # TODO: filter apps
    yield from get_subclasses(root_class)


def get_file_loc(klass):
    try:
        __, n = inspect.getsourcelines(klass)
    except (OSError, IOError):
        n = None
    try:
        f = inspect.getfile(klass)
    except TypeError:
        return ''
    else:
        if n is None:
            return f
        return f'{f}:{n}'


def get_templates():
    for template_sub in get_subclasses_for_apps(TemplateResponseMixin):
        if template_sub.template_name:
            pass


def template_exists(template_name, using=None):
    try:
        return get_template(template_name, using=using)
    except TemplateDoesNotExist:
        return False