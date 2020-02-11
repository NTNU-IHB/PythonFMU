from abc import ABC
from enum import Enum
from typing import Any, Optional
from xml.etree.ElementTree import Element, SubElement

from .enums import Fmi2Causality, Fmi2Initial, Fmi2Variability


class ScalarVariable(ABC):
    def __init__(
        self,
        name: str,
        causality: Optional[Fmi2Causality] = None,
        description: Optional[str] = None,
        initial: Optional[Fmi2Initial] = None,
        variability: Optional[Fmi2Variability] = None,
    ):
        self.__attrs = {
            "name": name,
            "valueReference": None,
            "description": description,
            "causality": causality,
            "variability": variability,
            "initial": initial,
            # 'canHandleMultipleSetPerTimeInstant': # Only for ME
        }

    @property
    def causality(self) -> Optional[Fmi2Causality]:
        return self.__attrs["causality"]

    @property
    def description(self) -> Optional[str]:
        return self.__attrs["description"]

    @property
    def initial(self) -> Optional[Fmi2Initial]:
        return self.__attrs["initial"]

    @property
    def name(self) -> str:
        return self.__attrs["name"]

    @property
    def value_reference(self) -> int:
        return self.__attrs["valueReference"]

    @value_reference.setter
    def value_reference(self, value: int):
        if self.__attrs["valueReference"] is not None:
            raise RuntimeError("Value reference already set.")
        self.__attrs["valueReference"] = value

    @property
    def variability(self) -> Optional[Fmi2Variability]:
        return self.__attrs["variability"]

    @staticmethod
    def requires_start(v) -> bool:
        return v.initial == Fmi2Initial.exact or \
               v.initial == Fmi2Initial.approx or \
               v.causality == Fmi2Causality.input or \
               v.causality == Fmi2Causality.parameter or \
               v.variability == Fmi2Variability.constant

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value.name if isinstance(value, Enum) else value)
        return Element("ScalarVariable", attrib)


class Real(ScalarVariable):
    def __init__(self, name: str, start: Optional[Any] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {"start": start}

    @property
    def start(self) -> Optional[Any]:
        return self.__attrs["start"]

    @start.setter
    def start(self, value: float):
        self.__attrs["start"] = value

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value)
        parent = super().to_xml()
        SubElement(parent, "Real", attrib)

        return parent


class Integer(ScalarVariable):
    def __init__(self, name: str, start: Optional[Any] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {"start": start}

    @property
    def start(self) -> Optional[Any]:
        return self.__attrs["start"]

    @start.setter
    def start(self, value: float):
        self.__attrs["start"] = value

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value)
        parent = super().to_xml()
        SubElement(parent, "Integer", attrib)

        return parent


class Boolean(ScalarVariable):
    def __init__(self, name: str, start: Optional[Any] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {"start": start}

    @property
    def start(self) -> Optional[Any]:
        return self.__attrs["start"]

    @start.setter
    def start(self, value: float):
        self.__attrs["start"] = value

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value).lower()
        parent = super().to_xml()
        SubElement(parent, "Boolean", attrib)

        return parent


class String(ScalarVariable):
    def __init__(self, name: str, start: Optional[Any] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {"start": start}

    @property
    def start(self) -> Optional[Any]:
        return self.__attrs["start"]

    @start.setter
    def start(self, value: float):
        self.__attrs["start"] = value

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value)
        parent = super().to_xml()
        SubElement(parent, "String", attrib)

        return parent
