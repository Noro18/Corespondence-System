from django.contrib.auth.mixins import AccessMixin

from apps.accounts.models import CustomUser


class RoleRequiredMixin(AccessMixin):
    allowed_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in self.allowed_roles:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class AdminMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN]


class AdministratorWorkerOnlyMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN_WORKER]


class AdministratorWorkerMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.ADMIN_WORKER]


class SekretariaduMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.SEKRETARIADU]


class PrezidenteMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.PREZIDENTE]


class StaffMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.STAFF]


class StaffOrSekretariaduMixin(RoleRequiredMixin):
    allowed_roles = [CustomUser.Role.ADMIN, CustomUser.Role.SEKRETARIADU, CustomUser.Role.STAFF]
