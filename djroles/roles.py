from django.conf import settings
from django.contrib.auth.models import Group

# TODO
# To już nie będzie potrzebne. Teraz jeśli jakaś grupa ma być uważana za rolę,
# to bezwzględnie musi się znaleźć w tabeli Roles.
DEFAULT_GROUPS = [group.name.lower() for group in Group.objects.all()]

class RoleError(Exception):
    """
    Base class for exceptions in this module.
    """
    pass

# TODO
# Albo zrobić wszsytko klasą, albo (co chyba lepsze) zrobić tylko funkcje
# w tym module. Odpowiednie rzeczy można za pomocą _ ukryć jako prywatne.
class Role(object):
    # TODO
    # To też nie będzie potrzebne. Informacje o rolach użytkownika wydobędę z
    # grup użytkownika, które należą do Roles.
    _role_groups = set(getattr(settings, "ROLE_GROUPS", DEFAULT_GROUPS))
    
    @classmethod
    def get_role(cls, user):
        """
        Retrieves the given user's role
        """
        # TODO
        # Dzięki mocy OneToOneField nie muszę robić intersection. Teraz 
        # wystarczy wyciągnąć z użytkownika te grupy, które są w Roles.
        # Tylko jedna operacja na bazie
        user_groups = set([group.name.lower() for group in user.groups.all()])
        user_role = cls._role_groups.intersection(user_groups)
        
        # TODO
        # Walidacja pozostanie niezbędna. Pytanie tylko czy robić to na tym
        # etapie, wcześniej, a może w kilku miejscach.
        if len(user_role) < 1:
            raise RoleError("The user is not a member of any role groups")
        elif len(user_role) > 1:
            raise RoleError("The user is a member of multiple role groups")
        else:
            return user_role.pop()

