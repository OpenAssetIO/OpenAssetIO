#
#   Copyright 2013-2021 The Foundry Visionmongers Ltd
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
"""
@namespace openassetio._core.objects
The OpenAssetIO API is built using the core FixedInterfaceObject class.
This provides python objects that reject the addition of any new
attributes at runtime, and provide type validation for their predefined
properties when their values are set.
"""

import copy
import inspect


__all__ = ["UntypedProperty", "TypedProperty", "FixedInterfaceObject"]


class UntypedProperty(object):
    """
    The Property classes form the basis for the FixedInterfaceObject.
    They implement a Python property, and store the data in the
    instances dataVar. Docstrings can also be provided to improve help()
    output.

    @param initVal, An initial value for the property if None is not
    supported.

    @param doc str, A docstring for the property that will be printed
    when help() is called on the object.

    @param dataVar str ['__dict__'] The instance dict attribute that
    should be used to hold the properties data. It defaults to the
    objects __dict__, but could be something else if de-coupled storage
    is desired.

    @param dataName str ['__<id(self)>'] The key to use when storing a
    value in dataVar. If omitted, this defaults to a prefixed version of
    the id of the object, though this may cause serialisation issues -
    so its recommended that this is set to something meaningful. Some
    objects use Metaclasses to take care of this automatically to avoid
    the developer having to manually match the dataName to the actual
    attribute name.

    @param order int [-1] A UI hint as to the 'natural ordering' for
    this property when it's displayed in a list.
    """

    def __init__(self, initVal=None, doc=None, dataVar=None, dataName=None, order=-1):
        super(UntypedProperty, self).__init__()
        self.__doc__ = doc
        self.initialValue = initVal
        self.dataVar = dataVar if dataVar else "__dict__"
        # I don't know how well this will serialize but its to avoid you always
        # having to name it twice. Though most Factories take care of this now.
        self.dataName = dataName if dataName else "__%s" % id(self)
        # This may be used for positioning in the ui, this should be > 0
        # as -1 indicates that it is unordered or ordering is not important
        self.order = order

    def __get__(self, obj, cls):
        # Allow access to ourself if we're called on the class
        if obj is None:
            return self
        return getattr(obj, self.dataVar).get(self.dataName, self.initialValue)

    def __set__(self, obj, value):
        getattr(obj, self.dataVar)[self.dataName] = value


class TypedProperty(UntypedProperty):
    """
    Extends the UntypedProperty to allow strict type checking of values.

    @param typ Class, Sets will be conformed to being instances of this
    type of None.

    @exception ValueError or other as per constructing an instance of
    the property's typ from the supplied value. ie: typ(value).
    """

    def __init__(self, typ, initVal=None, doc=None, dataVar=None, dataName=None, order=-1):
        if initVal is None:
            initVal = typ()
        super(TypedProperty, self).__init__(initVal, doc, dataVar, dataName, order)
        self.__doc__ = "[%s]" % typ.__name__
        if doc:
            self.__doc__ += " %s" % doc
        self.typ = typ

    def __set__(self, obj, value):
        if not isinstance(value, self.typ) and value is not None:
            value = self.typ(value)
        super(TypedProperty, self).__set__(obj, value)


class FixedInterfaceObject(object):
    """
    This class is a simple extension to object, to dis-allow get/set of
    any attributes not defined with the class. This can be useful to
    make introspectable objects with meaningful help() messages by
    creating data members like so:

    /code numCakes = TypedProperty(int, doc="Some member variable")
    edible = UntypedProperty() /endcode
    """

    def __init__(self):
        super(FixedInterfaceObject, self).__init__()

        # We need to set any default values of the properties here, so that they
        # will be available in the data var by default too

        def predicate(member):
            return isinstance(member, UntypedProperty)

        members = inspect.getmembers(self.__class__, predicate)
        for name, prop in members:
            if prop.initialValue is not None:
                setattr(self, name, copy.copy(prop.initialValue))

    def __getattr__(self, name):
        # This is only called if the attribute is not found by other means, ie: it
        # has not been defined in the class definition, etc...
        classname = self.__class__.__name__
        raise AttributeError("%s does not have an attribute '%s'" % (classname, name))

    def __setattr__(self, name, value):
        if name.startswith("_") or name in self.definedPropertyNames():
            object.__setattr__(self, name, value)
        else:
            classname = self.__class__.__name__
            raise AttributeError("%s does not have an attribute '%s'" % (classname, name))

    @classmethod
    def definedPropertyNames(cls):
        """
        @return list, A list of property names, sorted by their
        specified order.
        """

        def predicate(member):
            return isinstance(member, UntypedProperty)

        members = inspect.getmembers(cls, predicate)

        # We want to sort by the 'order' key if its greater than -1
        def sortFn(prop):
            return prop[1].order if prop[1].order > -1 else 9999999

        members.sort(key=sortFn)

        # Extract the names from the now sorted tuple list
        return [name for name, value in members]
