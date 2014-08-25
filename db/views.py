

class DatabaseMixin():
    """ Mixin for vanilla views to filter objects based on trips_year.

    Plugs into ModelViews. The url is a database url of the form
    /something/{{trips_year}}/something.

    TODO: handle requests for trips_years which are not in the database.
    They should give 404s? This must not mess up ListViews with no results.
    """

    def get_queryset(self):
        """ Get objects for requested trips_year """

        qs = super(DatabaseMixin, self).get_queryset()
        return qs.filter(trips_year=self.kwargs['trips_year'])

    


