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

    def to_list(self):
        return [self.x, self.y]

    @classmethod
    def from_list(cls, data):
        return cls(x=data[0], y=data[1])


class Transform2D(Atom):
    m11 = Float(0)
    m12 = Float(0)
    m13 = Float(0)
    m21 = Float(0)
    m22 = Float(0)
    m23 = Float(0)
    m31 = Float(0)
    m32 = Float(0)
    m33 = Float(0)

    def to_list(self):
        return [self.m11, self.m12, self.m13,
                self.m21, self.m22, self.m23,
                self.m31, self.m32, self.m33]

    @classmethod
    def from_list(cls, data):
        return cls(m11=data[0], m12=data[1], m13=data[2],
                   m21=data[3], m22=data[4], m23=data[5],
                   m31=data[6], m32=data[7], m33=data[8])

