from django.conf import settings

from .exceptions import RoleError
from .models import Role

DEFAULT_REGISTRY = (
    "get_queryset",
    "get_serializer_class",
    "perform_create",
    "perform_update",
    "perform_destroy",
)


class RoleViewSetMixin(object):
    """
    A ViewSet mixin that parameterizes DRF methods over roles
    """
    _viewset_method_registry = set(getattr(settings, "VIEWSET_METHOD_REGISTRY",
        DEFAULT_REGISTRY))

    def _call_role_fn(self, fn, *args, **kwargs):
        """Attempts to call a role-scoped method"""
        try:
            role = Role.objects.get_role(self.request.user)
            role_fn = "{}_for_{}".format(fn, role.name)
            return getattr(self, role_fn)(*args, **kwargs)
        except (AttributeError, RoleError):
            return getattr(super(RoleViewSetMixin, self), fn)(*args, **kwargs)

def register_fn(fn):
    """Dynamically adds fn to RoleViewSetMixin"""
    def inner(self, *args, **kwargs):
        return self._call_role_fn(fn, *args, **kwargs)
    setattr(RoleViewSetMixin, fn, inner)

# Registers whitelist of ViewSet fns to override
for fn in RoleViewSetMixin._viewset_method_registry:
    register_fn(fn)
