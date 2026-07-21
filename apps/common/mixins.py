from django.contrib.auth.mixins import AccessMixin

from apps.accounts.models import CustomUser


class RoleRequiredMixin(AccessMixin):
    allowed_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if request.user.role not in self.allowed_roles:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AdminMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN]


class SekretariaduMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.SEKRETARIADU]


class PrezidenteMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.PREZIDENTE]


class StaffMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.STAFF]
