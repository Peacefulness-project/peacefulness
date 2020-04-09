__world__ = None


def set_world(world):
    global __world__
    __world__ = world
    # print(__world__)


def get_world():
    return __world__


