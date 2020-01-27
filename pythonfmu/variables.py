from abc import ABC, abstractmethod
from enum import Enum
from xml.etree.ElementTree import Element, SubElement

from .enums import Fmi2Causality, Fmi2Initial, Fmi2Variability


class ScalarVariable(ABC):

    __vr_counter = 0

    def __init__(
        self, 
        name, 
        causality=None, 
        description=None, 
        initial=None,
        variability=None,
    ):
        self.__attrs = {
            'name': name,
            'valueReference': ScalarVariable.__get_and_increment_vr(),
            'description': description,
            'causality': causality,
            'variability': variability,
            'initial': initial,
            # 'canHandleMultipleSetPerTimeInstant': # Only for ME
        }

    @staticmethod
    def __get_and_increment_vr():
        vr = ScalarVariable.__vr_counter
        ScalarVariable.__vr_counter += 1
        return vr

    @property
    def causality(self):
        return self.__attrs['causality']

    @property
    def description(self):
        return self.__attrs['description']

    @property
    def initial(self):
        return self.__attrs['initial']

    @property
    def name(self):
        return self.__attrs['name']

    @property
    def variability(self):
        return self.__attrs['variability']

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value.name if isinstance(value, Enum) else value)
        return Element('ScalarVariable', attrib)


class Real(ScalarVariable):
    def __init__(self, name, start=None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {
            'start': start
        }

    @property
    def start(self):
        return self.__attrs['start']

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value)
        parent = super().to_xml()
        SubElement(parent, 'Real', attrib)

        return parent


class Integer(ScalarVariable):
    def __init__(self, name, start=None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {
            'start': start
        }

    @property
    def start(self):
        return self.__attrs['start']

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value)
        parent = super().to_xml()
        SubElement(parent, 'Integer', attrib)

        return parent


class Boolean(ScalarVariable):
    def __init__(self, name, start=None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {
            'start': start
        }

    @property
    def start(self):
        return self.__attrs['start']

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value)
        parent = super().to_xml()
        SubElement(parent, 'Boolean', attrib)

        return parent


class String(ScalarVariable):
    def __init__(self, name, start=None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {
            'start': start
        }

    @property
    def start(self):
        return self.__attrs['start']

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value)
        parent = super().to_xml()
        SubElement(parent, 'String', attrib)

        return parent
