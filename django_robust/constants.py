from enum import Enum, auto, EnumMeta, IntEnum

from django.core.checks import Error, Warning


class CodeDispatcher(EnumMeta):

    def __new__(cls, classname, bases, classdict, **kwds):
        for k, v in classdict.items():
            if v is None:
                pass
        return super().__new__(cls, classname, bases, classdict, **kwds)


class CodeDispatcher(IntEnum, metaclass=CodeDispatcher):
    def __init_subclass__(cls, *, prefix, constructor, app_name, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.prefix = prefix
        cls.app_name = app_name  # TODO: automatically derive
        cls.constructor = constructor

    def __str__(self):
        return f'{self.app_name}.{self.prefix}{self.value:03}'

    def __call__(self, msg, hint=None, obj=None):
        return self.constructor(
            msg=msg,
            hint=hint,
            obj=obj,
            id=str(self)
        )  # pass id

class RobustError(CodeDispatcher, app_name='django_robust', prefix='E', constructor=Error):
    pass

class RobustWarning(CodeDispatcher, app_name='django_robust', prefix='W', constructor=Warning):
    TemplateDoesNotExist = auto()
    InvalidSuccessUrl = auto()