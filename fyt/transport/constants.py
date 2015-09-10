import types
from fyt.transport.models import Stop

# TODO: move to manager
# TODO: make these immutable, or something. The problem is 
# that objects without pks don't compare as equal in testing.


class ConstantStop(Stop):
    def __eq__(self, other):
        return (self.name == other.name and self.location == other.location)

def Hanover():
    return ConstantStop(
        name='Hanover, NH', address='6 N Main St, Hanover, NH 03755'
    )

def Lodge():
    return ConstantStop(
        name='The Moosilauke Ravine Lodge', address='43.977253,-71.8154831'
    )

