
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required

# TODO: ! SEE http://django-braces.readthedocs.org/en/latest/index.html
# for identical actions!

class GraderPermissionRequiredMixin():
    """ Restrict access to users with grader permission """

    @method_decorator(permission_required('user.can_grade_applications', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(GraderPermissionRequiredMixin, self).dispatch(*args, **kwargs)


class DatabasePermissionRequiredMixin():
    """ Restrict access to users with database permission """
    
    @method_decorator(permission_required('user.can_access_db', raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        return super(DatabasePermissionRequiredMixin, self).dispatch(*args, **kwargs)

              
class LoginRequiredMixin():
    """ Class view mixin which adds login protection """

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
        

    
