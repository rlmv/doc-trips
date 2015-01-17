

from braces.views import PermissionRequiredMixin, LoginRequiredMixin

from db.views import TripsYearMixin

"""
Grading portal, redirects to next app to grade. 

Restricted to directorate.
"""


""" 
Grade form - read and input. 

Redirect to grading portal on successful post.
"""


"""
Create/edit this year's application.

Used by directors to edit application questions. 
SHOULD be hidden once the application is open.
"""

class CreateCrooApplication(LoginRequiredMixin, PermissionRequiredMixin, TripsYearMixin):
    
    permission_required = 'permission.can_create_croo_application'
    redirect_unauthenticate_users = True
    raise_exception = True 


"""
Database views of croo apps

INdex view - sortable by safety dork/croo type.
How does croo selection work? Is it blind? 

Each app should have a link to the app's grading page. Should there be a way to 
add an app back into the blind grading pool?

Directorate (directors?) can approve applications/assign them to croos. 

Access/permissions page can link to here for removing/adding to the 'Croo' group.

"""



