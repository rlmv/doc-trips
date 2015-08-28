from functools import wraps

def cache_as(name):
    """
    Store a method result on an object. Use carefully,
    on things which should be immutable.

    Eg,

    @cache_as('_size')
    def size(self):
        # expensize computation
 
    The result of size() will be stored in a property '_size'
    on the object. The next time size() is called, '_size'
    will be returned instead.

    Note that this DOES NOT perform any cache invalidation!
    TODO: invalidate if the model is saved/changed?
    """
    def decorator(func):
        @wraps(func)
        def wrapper(obj, *args, **kwargs):
            if not hasattr(obj, name):
                setattr(obj, name, func(obj, *args, **kwargs))
            return getattr(obj, name)
        return wrapper
    return decorator


def preload(obj, name, value):
    """
    Companion to cache_as. Stores a value so that a method
    cached under the same name returns the preloaded value
    instead of calling the method.

    Useful for doing batch computations, particularly the
    transport matrices.
    """
    setattr(obj, name, value)
    
