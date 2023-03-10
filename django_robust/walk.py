from operator import attrgetter
from typing import TypeVar, Iterable

from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.template.loader_tags import IncludeNode

from django_robust.templates import is_simple_constant

T = TypeVar('T')

def walk(item : T, *items: T, children_field=iter) -> Iterable[T]:
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


def template_walker(template, using=None):
    if isinstance(template, str):
        template = get_template(template, using=using)
    if hasattr(template, 'template'):
        # loaded template
        template = template.template
    walker = walk(*template.compile_nodelist())
    try:
        node = next(walker)
        while True:
            yield node
            old_node = node
            node = None
            # look for sub-blocks, includes, etc.
            if isinstance(old_node, IncludeNode):
                template_name = is_simple_constant(old_node.template)
                if template_name is not None:
                    try:
                        template = get_template(template, using=using)
                    except TemplateDoesNotExist:
                        pass  # too bad, can not inspect
                    else:
                        node = walker.send(template.template.compile_node_list())
            if node is None:
                node = next(walker)
    except StopIteration:
        pass