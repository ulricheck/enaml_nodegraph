from atom.api import Atom, Float


class Point2D(Atom):
    x = Float(0)
    y = Float(0)

    def __repr__(self):
        return '<Point2D (%f, %f)>' % (self.x, self.y)

    def __add__(self, other):
        if isinstance(other, Point2D):
            return Point2D(x=self.x + other.x, y=self.y + other.y)
        else:
            raise TypeError("Addition for type %s not implemented." % type(other))

    def __radd__(self, other):
        if isinstance(other, Point2D):
            return Point2D(x=other.x + self.x, y=other.y + self.y)
        else:
            raise TypeError("Addition for type %s not implemented." % type(other))

    def __sub__(self, other):
        if isinstance(other, Point2D):
            return Point2D(x=self.x - other.x, y=self.y - other.y)
        else:
            raise TypeError("Subtraction for type %s not implemented." % type(other))

    def __rsub__(self, other):
        if isinstance(other, Point2D):
            return Point2D(x=other.x - self.x, y=other.y - self.y)
        else:
            raise TypeError("Subtraction for type %s not implemented." % type(other))

