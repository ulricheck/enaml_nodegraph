import logging

from atom.api import (Atom, Bool, Int, Float, Str, Str, Enum,
                      List, Dict, ContainerList, Typed, Instance)

log = logging.getLogger(__name__)


def serialize(archive, member, value):
    if isinstance(member, (Bool, Int, Float, Str, Str)):
        archive[member.name] = value
    # @todo only correct for simple types (Int, Bool, Float, Str, Str)
    elif isinstance(member, (List, ContainerList)):
        archive[member.name] = value
    # @todo only correct for simple types (Int, Bool, Float, Str, Str)
    elif isinstance(member, Dict):
        archive[member.name] = value
    elif isinstance(member, Enum):
        archive[member.name] = value
    elif isinstance(member, (Typed, Instance)):
        log.warning("Cannot serialize Typed/Instance member: %s -> %s" % (member.name, type(member)))
    else:
        log.warning("Unknown member type: %s -> %s" % (member.name, type(member)))


def deserialize(archive, member):

    if isinstance(member, (Bool, Int, Float, Str, Str)):
        return archive[member.name]
    # @todo only correct for simple types (Int, Bool, Float, Str, Str)
    elif isinstance(member, (List, ContainerList)):
        return archive[member.name]
    # @todo only correct for simple types (Int, Bool, Float, Str, Str)
    elif isinstance(member, Dict):
        return archive[member.name]
    elif isinstance(member, Enum):
        return archive[member.name]
    elif isinstance(member, (Typed, Instance)):
        log.warning("Cannot serialize Typed/Instance member: %s -> %s" % (member.name, type(member)))
    else:
        log.warning("Unknown member type: %s -> %s" % (member.name, type(member)))
    return None


class Attributes(Atom):

    def serialize(self, archive):
        for name, member in self.members().items():
            serialize(archive, member, getattr(self, name))

    def deserialize(self, archive):
        for name, member in self.members().items():
            if name in archive:
                setattr(self, name, deserialize(archive, member))


class GraphItem(Atom):

    attributes = Instance(Attributes)

    def serialize(self, archive):
        if self.attributes is not None:
            attrs = archive.setdefault('attributes', {})
            self.attributes.serialize(attrs)

    def deserialize(self, archive):
        if self.attributes is not None:
            self.attributes.deserialize(archive.get('attributes', {}))
