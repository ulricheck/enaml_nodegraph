from atom.api import Atom, Float


class Point2D(Atom):
    x = Float(0)
    y = Float(0)

    def __repr__(self):
        return '<Point2D (%f, %f)>' % (self.x, self.y)
