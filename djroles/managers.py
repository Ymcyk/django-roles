from django.db import models
from django.db.utils import IntegrityError
from django.contrib.auth.models import Group, Permission

from .exceptions import RoleError

class RoleManager(models.Manager):
    def create_role(self, name, description=None):
        """
        Create Role and Group object, if not exist.
        IntegrityError will be raised when craeting more than one Role, with
        the same name.
        """
        group = self._get_group(name)
        role = self.create(group=group, description=description)
        return role

    def _get_group(self, name):
        group = Group.objects.get_or_create(name=name)[0]
        return group

    def get_role(self, user):
        """
        Get role for given user
        """
        user_role = self.filter(group=user.groups.all())
        self._check_role_unique(user_role)

        return user_role.get()

    def _check_role_unique(self, user_role):
        """
        Error if roles number in queryset is not one
        """
        group_number = user_role.count()

        if group_number < 1:
            raise RoleError('User is not a memeber of any role group')
        elif group_number > 1:
            raise RoleError('User is a member of multiple groups')
