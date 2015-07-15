import types
from doc.transport.models import Stop

# TODO: move to manager
# TODO: make these immutable, or something. The problem is 
# that objects without pks don't compare as equal in testing.


class ConstantStop(Stop):
    def __eq__(x, y):
        return (x.name == y.name and x.address == y.address)

def Hanover():
    return ConstantStop(
        name='Hanover, NH', address='Hanover, NH'
    )

def Lodge():
    return ConstantStop(
        name='The Moosilauke Ravine Lodge', address='43.977253,-71.8154831'
    )

