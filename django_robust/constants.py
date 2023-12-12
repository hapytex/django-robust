from enum import IntEnum
from django.apps import apps

from django.core.checks import Debug, Error, Warning, Info, Critical
from django.utils.safestring import SafeString
from itertools import count
from django.core.checks import register

from django.utils.translation import gettext_lazy


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
        return '&#xfffd;'  # �


MISSING = Untruthfull()  # for fast lookups
UNKNOWN = Unknown('<unknown>')


class CodeDispatcher(IntEnum):
    def __new__(cls, val, hint=None, tags=None):
        if isinstance(val, (int, cls)):
            return super().__new__(cls, val)
        else:
            idx = next(cls.dispatcher)
            result = int.__new__(cls, idx)
            result._value_ = idx
            if isinstance(val, str):
                val = gettext_lazy(val)
            result.message = val
            if isinstance(hint, str):
                hint = gettext_lazy(hint)
            result.hint = hint
            result.tags = set(tags or ())
            return result


    def __init_subclass__(cls, *, constructor=None, app_name=None, prefix=None, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.app_name = app_name or apps.get_containing_app_config(cls.__module__).label
        if constructor is None:
            constructors = (Debug, Error, Warning, Info, Critical)
            name = cls.__name__
            for constructor in constructors:
                if name.endswith(constructor.__name__):
                    break
            else:
                raise ValueError('The constructor can not be determined based on the name of the enum class.')
        cls.constructor = constructor
        if prefix is None:
            assert isinstance(constructor, type), TypeError('The constructor needs to be a class.')
            prefix = constructor.__name__[:1].upper()
        cls.prefix = prefix
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

    def register_check(self, func):
        return register(func, *self.tags)


class RobustError(CodeDispatcher):
    pass

class RobustWarning(CodeDispatcher):
    TemplateDoesNotExist = (
        'Template {template_name} defined on {template_sub} {template_loc} does not exist',
        'Check if the template name {template_name} points to a valid file'
    )
    InvalidSuccessUrl = (
        'Template {success_url} defined on {form_sub} {form_loc} does not exist',
        'Check if the template name {success_url} points to a valid view'
    )
    NoQuerySetConfigured = (
        '',
        'SingleObjectMixin',
    )
    InvalidTemplateUrlViewName = (
        '',  # TODO
        ''
    )

class RobustDebug(CodeDispatcher):
    NoTransTagInTemplate = (
        '',
        ''
    )

class RobustInfo(CodeDispatcher):
    pass

class RobustCritical(CodeDispatcher):
    pass