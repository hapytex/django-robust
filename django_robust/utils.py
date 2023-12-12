import inspect
from itertools import islice
from operator import attrgetter
from typing import Iterable, TypeVar, Optional, Type, Union, Callable
from typing import Iterable, TypeVar, Optional

from django.apps import apps
from django.http import HttpRequest
from django.template import TemplateDoesNotExist, Node
from django.template import TemplateDoesNotExist
from django.template.base import FilterExpression
from django.template.loader import get_template
from django.views.generic.base import TemplateResponseMixin

from django_robust.constants import MISSING, UNKNOWN, Untruthfull

T = TypeVar('T')
Q = TypeVar('Q')

def or_unknown(f:Callable[..., T], *args, _unknown:Q=UNKNOWN, _exception_type_filter=BaseException, **kwargs) -> Union[T, Q]:
    try:
        result = f(*args, **kwargs)
        if result is MISSING:
            return _unknown
        return result
    except _exception_type_filter:
        return _unknown

def format_file_loc(filename:Optional[str], row:Optional[int]=None, colstart:Optional[int]=None, colstop:Optional[int]=None) -> str:
    if filename is not None:
        if row is not None:
            if colstart is not None:
                if colstop is not None and colstart != colstop:
                    return f'{filename}:{row}:{colstart}–{colstop}'
                return f'{filename}:{row}:{colstart}'
            return f'{filename}:{row}'
        return filename
    return UNKNOWN

def get_node_file_loc(node:Node) -> str:
    token = node.token
    return format_file_loc(getattr(node, 'origin', None), token.lineno, *token.position)

def all_in_stack(type_filter: Type[T], var_name='self') -> Iterable[T]:
    for item in islice(inspect.stack(), 1):
        # walk the stack and look for the request
        obj = item.frame.f_locals.get(var_name, MISSING)
        if obj is not MISSING and isinstance(obj, type_filter):
            yield obj

def look_in_stack(type_filter: Type[T], var_name='self') -> Union[T, Untruthfull]:
    for item in all_in_stack(type_filter=type_filter, var_name=var_name):
        return item
    return MISSING


def get_request_from_stack(type_filter: Type[T]=HttpRequest, var_name='request') -> Union[T, Untruthfull]:
    return look_in_stack(type_filter=type_filter, var_name=var_name)


def get_template_node_from_stack(var_name:str='self') -> Union[Node, Untruthfull]:
    return look_in_stack(Node, var_name=var_name)


def get_template_location_from_stack(var_name:str='self') -> str:
    return get_node_file_loc(get_template_node_from_stack(var_name=var_name))


class AppConfigFilter:
    def __init__(self, items):
        pass



def get_app_configs(app_configs=None):
    if app_configs is None:
        return apps.get_app_configs()
    return app_configs

def get_subclasses(root_class: Type[T]) -> Iterable[Type[T]]:
    yield root_class
    seen = gen = {root_class}
    while gen:
        next_gen = {sub for klass in gen for sub in klass.__subclasses__() if sub not in seen}
        yield from next_gen
        seen.update(next_gen)
        gen = next_gen


def get_subclasses_for_apps(root_class: Type[T], app_configs=None) -> Iterable[Type[T]]:
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