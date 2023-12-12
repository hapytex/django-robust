import logging

from django_robust.constants import UNKNOWN, Untruthfull
from django_robust.utils import get_request_from_stack, or_unknown, get_template_node_from_stack, \
    get_template_location_from_stack

logger = logging.getLogger('templates')

class InvalidVarException(Untruthfull, str):
    DEFAULT_MESSAGE = "Missing variable {{{{ {missing_str} }}}} at {loc} for path {full_path}"

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
                message = self.DEFAULT_MESSAGE.format(
                    missing_str=missing_str,
                    loc=loc,
                    full_path=full_path
                )
                logger.error(message)
            except:
                pass
        # return the current string for rendering, we thus can still print debug information
        return self

    def format(self, missing, *args, **kwargs) -> str:
        return self.__mod__(missing)


    def __bool__(self):
        # Trick the system in believing there is content
        return True

    def __contains__(self, search):
        # Trick the system in believing the strings needs to be formatted
        return "%s" in search or super().__contains__(search)