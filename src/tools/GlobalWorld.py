__world__ = None


def set_world(world):
    global __world__
    __world__ = world


def get_world():
    return __world__


