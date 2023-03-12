from enum import auto, EnumMeta, IntEnum

from django.core.checks import Debug, Error, Warning, Info, Critical
from django.utils.safestring import SafeString
from itertools import count


class Untruthfull:
    def __getitem__(self, item) -> 'Untruthfull':
        # to make optional computations convenient
        # x[y] is x for any y
        return self
    def __getattr__(self, item) -> 'Untruthfull':
        # to make optional computations convenient
        # x.y is x for any y
        return self

    def __call__(self, *args, **kwargs) -> 'Untruthfull':
        # to make optional computations convenient
        # x() is x
        return self
    def __bool__(self):
        # for truthiness checks
        return False

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return hash(None) + 1

class Unknown(Untruthfull, SafeString):
    def __html__(self):
        return '&#xfffd;'


MISSING = Untruthfull()  # for fast lookups
UNKNOWN = Unknown('<unknown>')


class CodeDispatcher(IntEnum):
    def __new__(cls, val, hint=None):
        if isinstance(val, (int, cls)):
            return super().__new__(cls, val)
        else:
            idx = next(cls.dispatcher)
            result = int.__new__(cls, idx)
            result._value_ = idx
            result.message = val
            result.hint = hint
            return result


    def __init_subclass__(cls, *, constructor, app_name, prefix=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if prefix is None:
            prefix = constructor.__name__[:1].upper()
        cls.prefix = prefix
        cls.app_name = app_name  # TODO: automatically derive
        cls.constructor = constructor
        cls.dispatcher = count(1)

    def __str__(self):
        return f'{self.app_name}.{self.prefix}{self.value:03}'

    def __call__(self, obj=None, **kwargs):
        kwargs['obj'] = obj
        hint = self.hint
        if hint is not None:
            hint = hint % kwargs
        return self.constructor(
            msg=self.msg % kwargs,
            hint=hint,
            obj=obj,
            id=str(self)
        )  # pass id

class RobustError(CodeDispatcher, app_name='django_robust', constructor=Error):
    pass

class RobustWarning(CodeDispatcher, app_name='django_robust', constructor=Warning):
    TemplateDoesNotExist = (
        'Template {template_name} defined on {template_sub} {template_loc} does not exist',
        'Check if the template name {template_name} points to a valid file'
    )
    InvalidSuccessUrl = (
        'Template {success_url} defined on {form_sub} {form_loc} does not exist',
        'Check if the template name {success_url} points to a valid view'
    )
    InvalidTemplateUrlViewName = (
        '',  # TODO
        ''
    )

class RobustDebug(CodeDispatcher, app_name='django_robust', constructor=Debug):
    NoTransTagInTemplate = (
        '',
        ''
    )

class RobustInfo(CodeDispatcher, app_name='django_robust', constructor=Info):
    pass

class RobustCritical(CodeDispatcher, app_name='django_robust', constructor=Critical):
    pass