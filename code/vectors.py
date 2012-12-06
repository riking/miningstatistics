from collections import namedtuple

_Vector = namedtuple("_Vector", ("x", "y", "z"))

class Vector(_Vector):

    __slots__ = ()

    def __add__(self, other):
        return Vector(self[0] + other[0], self[1] + other[1], self[2] + other[2])
    def __sub__(self, other):
        return Vector(self[0] - other[0], self[1] - other[1], self[2] - other[2])
    def __mul__(self, other):
        return Vector(self[0] * other[0], self[1] * other[1], self[2] * other[2])
    def __eq__(self, other):
    	return self[0] == other[0] and self[1] == other[1] and self[2] == other[2]
