from .models import Stop


class ConstantStop(Stop):
    """
    Constant, unsavable Stop objects.

    Since objects without pks cannot be compared well, we
    override ``__eq__`` to just check ``name`` and ``location``.

    TODO: move these to a manager?
    """
    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        return

    def __eq__(self, other):
        return (self.name == other.name and self.location == other.location)


def Hanover():
    return ConstantStop(
        name='Hanover, NH',
        address='6 N Main St, Hanover, NH 03755'
    )


def Lodge():
    return ConstantStop(
        name='The Moosilauke Ravine Lodge',
        address='43.977253,-71.8154831'
    )
