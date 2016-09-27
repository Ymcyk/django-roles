from django.test import TestCase

from .models import Role
from .exceptions import RoleError

def create_role(name, description=None):
        name = name
        description = description
        return Role.objects.create_role(name=name, description=description)

class RoleTest(TestCase):
    def test_role_creation(self):
        # prepare
        name = 'test_role'
        description = 'test_description'
        # do
        create_role(name, description)
        # check
        retriven_role = Role.objects.get(group__name=name)
        self.assertEqual(str(retriven_role), name)

    def test_group_created_with_role(self):
        # prepare
        from django.contrib.auth.models import Group
        name = 'test_role'
        # do
        create_role(name)
        # check
        group = Group.objects.filter(name=name)
        self.assertTrue(bool(group), msg='Group with same name wasn\'t created')

    def test_group_with_role_permission(self):
        # prepare
        from django.contrib.auth.models import Permission, Group
        name = 'test_name'
        # do
        create_role(name)
        # check
        group = Group.objects.get(name=name)
        group_perm = group.permissions.filter(codename='has_role')
        self.assertTrue(bool(group_perm), msg='Group don\'t have has_role')

    def test_group_deleted_with_role(self):
        # prepare
        from django.contrib.auth.models import Group
        name = 'test_role'
        # do
        role = create_role(name)
        role.delete()
        # check
        group = Group.objects.filter(name=name)
        self.assertFalse(bool(group), msg='Group wasn\'t deleted with role')

    def test_create_role_with_not_unique_name(self):
        # prepare
        name = 'test_role'
        # do
        create_role(name=name)
        # check
        with self.assertRaises(RoleError) as ie:
            create_role(name)
        
    def test_get_role_on_user_wihout_role(self):
        # prepare
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='jan')
        # do
        # check
        with self.assertRaises(RoleError) as re:
            Role.objects.get_role(user)

    def test_user_in_group_after_give_role(self):
        # prepare
        from django.contrib.auth.models import User, Group
        user = User.objects.create_user(username='jan')
        role = create_role('test_name')
        # do
        role.give_role(user)
        # check
        group = user.groups.filter(name='test_name')
        self.assertTrue(bool(group), msg='User not in role group')

    def test_user_have_role_after_give_role(self):
        # prepare
        from django.contrib.auth.models import User
        role = create_role('test_name')
        user = User.objects.create_user(username='jan')
        # do
        role.give_role(user)
        # check
        user_role = Role.objects.get_role(user)
        self.assertEqual(role, user_role, msg='User don\'t have role')

    def test_user_without_group_after_delete(self):
        # prepare
        from django.contrib.auth.models import User, Group, Permission
        name = 'test_name'
        role = create_role(name)
        user = User.objects.create_user(username='jan')
        role.give_role(user)
        role_group = user.groups.filter(name=name)
        self.assertTrue(bool(role_group), msg='User don\'t have group')
        # do
        role.delete()
        # check
        role_group = user.groups.filter(name=name)
        self.assertFalse(bool(role_group), msg='User have role group')

    def test_cant_give_user_more_than_one_role(self):
        # prepare
        from django.contrib.auth.models import User
        role = create_role('test_name')
        role2 = create_role('second_name')
        user = User.objects.create_user(username='jan')
        # do
        role.give_role(user)
        # check
        with self.assertRaises(RoleError):
            role2.give_role(user)

    def test_user_have_role_permissions(self):
        # prepare
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='jan')
        role = create_role('test_name')
        # do
        role.give_role(user)
        # check
        self.assertTrue(user.has_perm('djroles.has_role'))

    def test_user_dont_have_role_permissions_after_role_delete(self):
        # prepare
        from django.contrib.auth.models import User
        user = User.objects.create_user(username='jan')
        role = create_role('test_name')
        # do
        role.give_role(user)
        role.delete()
        # check
        self.assertFalse(user.has_perm('drf_roles.has_role'))
