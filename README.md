# `django-robust`

Robust checking of Django properties. Currently, Django allows way too many problems that are eventually found when running the software.

Implemented checks:

 - check if the `template_name` in subclasses of the `TemplateResponseMixin` point to a *valid* template file (W001);
 - check if the view names in `success_url` (W002);
 - ...