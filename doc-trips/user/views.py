
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required

class GraderPermissionRequiredMixin():
    """ Restrict access to users with grader permission """

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(GraderPermissionRequiredMixin, cls).as_view(*args, **kwargs)
        return permission_required(view, 'user.can_grade_applications', 
                                   raise_exception=True)

                      

    
