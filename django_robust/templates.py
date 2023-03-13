import logging
from typing import Optional

from django.template.base import FilterExpression

from django_robust.utils import get_request_from_stack, or_unknown, get_template_location_from_stack

logger = logging.getLogger('templates')

class InvalidVarException(str):
    # prevent reporting the same exception multiple times, and thus eventually flood sentry for example
    already = set()
    # this does NOT work for variables with ignore_failures=True, like {% for ... in ... %}

    def __mod__(self, missing, *args, **kwargs):
        missing_str = or_unknown(str, missing)
        request = or_unknown(get_request_from_stack)
        path = request.path
        full_path = request.get_full_path()
        loc = or_unknown(get_template_location_from_stack)
        key = (path, loc, missing_str)
        show = key not in self.already
        if show:
            # prevent reporting the same problem again
            self.already.add(key)
            try:
                # wrap in try-except to prevent that exceptions trigger a 500
                message = f"Missing variable {{{{ {missing_str} }}}} at {loc} for path {full_path}"
                logger.error(message)
            except:
                pass
        # return the current string for rendering, we thus can still print debug information
        return self

    def __bool__(self):
        # Trick the system in believing there is content
        return True

    def __contains__(self, search):
        # Trick the system in believing the strings needs to be formatted
        return "%s" in search or super().__contains__(search)



def is_simple_constant(expr: FilterExpression) -> Optional[str]:
    if not expr.is_var and not expr.filters:
        return expr.var
    # otherwise, we return None