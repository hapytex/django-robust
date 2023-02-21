# `django-robust`

Robust checking of Django properties. Currently, Django allows way too much problems that are eventually found when running the software.

Implemented checks:

 - check if the `template_name` in subclasses of the `TemplateResponseMixin` point to a *valid* template file (W001);
 - check if the view names indeed are correct in template files (W002);
 - ...