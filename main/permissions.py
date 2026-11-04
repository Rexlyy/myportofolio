from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSkillEditorOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        # GET, HEAD, OPTIONS dapat diakses semua orang
        if request.method in SAFE_METHODS:
            return True

        # Operasi selain read membutuhkan login
        if not request.user.is_authenticated:
            return False

        # POST hanya boleh dilakukan superuser
        if request.method == 'POST':
            return request.user.is_superuser

        return True

    def has_object_permission(self, request, view, obj):

        # Read dapat dilakukan semua orang
        if request.method in SAFE_METHODS:
            return True

        # DELETE hanya boleh dilakukan superuser
        if request.method == 'DELETE':
            return request.user.is_superuser

        # PUT dan PATCH boleh dilakukan superuser
        # atau user yang memiliki permission change_skill
        if request.method in ['PUT', 'PATCH']:
            return (
                request.user.is_superuser
                or request.user.has_perm('main.change_skill')
            )

        return False