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

from ._core.objects import UntypedProperty


__all__ = ['SpecificationFactory']


class SpecificationFactory(type):
    """
    The Factory provides facility to create Specifications of the most
    derived class. Useful when restoring data from an @ref entity for
    specific use.
    """

    classMap = {}

    def __new__(cls, name, bases, namespace):

        # Make sure properties have a suitable data name and store
        for key, value in namespace.items():
            if isinstance(value, UntypedProperty):
                value.dataVar = '_data'
                value.dataName = key

        newcls = super(SpecificationFactory, cls).__new__(cls, name, bases, namespace)
        if not hasattr(newcls, '__factoryIgnore'):
            if newcls._type:
                key = newcls.generateSchema(newcls._prefix, newcls._type)
            else:
                key = newcls._prefix
            cls.classMap[key] = newcls
        return newcls

    @classmethod
    def instantiate(cls, schema, data):
        """
        Creates a new Specification that contains the supplied data. The
        most derived class that matches the schema will be used. If no
        class has been registered with the exact scheme, then attempts
        will be made to find a class that matches the prefix. If all
        attempts fail, a @ref openassetio.Specification.SpecificationBase will be used.
        """

        from .Specification import SpecificationBase, Specification

        if not schema:
            return None

        customCls = cls.classMap.get(schema, None)
        prefix, type = Specification.schemaComponents(schema)
        if not customCls:
            customCls = cls.classMap.get(prefix)
        if customCls:
            instance = customCls(data)
            instance._setSchema(schema)
            instance._type = type
            return instance
        else:
            ## @todo re-instate logging for missing custom class
            return SpecificationBase(schema, data)

    @classmethod
    def upcast(cls, specification):
        schema = specification.schema()
        return cls.instantiate(schema, specification.data(copy=False))
