from apps.users.models import User


class CompanyScopedQuerySetMixin:
    """Automatically scopes a ModelViewSet's queryset to request.user.company.

    Super Admins see everything; everyone else only ever sees rows whose
    `company` FK matches their own company. This is the enforcement point
    that guarantees Company A can never read/write Company B's data — every
    viewset for a tenant-owned model (User, Project, Task, ...) must use it.
    Newly created objects are automatically stamped with the caller's company.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.role == User.Role.SUPER_ADMIN:
            return queryset
        return queryset.filter(company_id=user.company_id)

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)
