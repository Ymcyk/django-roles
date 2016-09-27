from django.db import models 
from django.contrib.auth.models import User, Group, Permission

from .managers import RoleManager
from .exceptions import RoleError

class Role(models.Model):
    """
    Model to identity role groups.
    """
    group = models.OneToOneField(
            Group,
            primary_key=True,
            on_delete=models.CASCADE,
            )
    description = models.CharField(
            'description', 
            max_length=250,
            null=True,
            )

    class Meta:
        # has_role - group with this permission is role
        permissions = (
            ('has_role', 'Role permission'),
        )

    objects = RoleManager()

    def save(self, *args, **kwargs):
        """
        With has_role permission group is recognized as role.
        Group with a role can't be in other role.
        """
        if self._is_group_a_role():
            raise RoleError('This group is already a role.')
        self._give_group_role_permission()
        super(type(self), self).save(*args, **kwargs)

    def _give_group_role_permission(self):
        permission = Permission.objects.get(codename='has_role')
        self.group.permissions.add(permission)

    def _is_group_a_role(self):
        return bool(self.group.permissions.filter(codename='has_role'))

    def __str__(self):
        return self.group.name
    # TODO
    # Zabronienie dodawania użytkownika do grupy, która jest rolą, jeśli
    # użykownik już takową posiada
    def give_role(self, user):
        """
        Give role to user without a role.
        """
        # Odświeżanie jest konieczne. Sprawdzanie permissions (jak has_perm)
        # powoduje cachowanie ich w obiekcie. W tym przypadku bez odświeżenia
        # wywołanie po sobie give_user będzie zwracać to samo.
        # Tym sposobem możliwe by było nadanie dwóch różnych grup
        ref_user = User.objects.get(id=user.id)        
        if ref_user.has_perm('drf_roles.has_role'):
            raise RoleError('This user has role')
        ref_user.groups.add(self.group)

from djroles import signals

