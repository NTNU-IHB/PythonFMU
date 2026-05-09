"""Classes describing interface type."""
from abc import ABC
from typing import Any, Optional
from xml.etree.ElementTree import Element, SubElement


class SimpleType(ABC):
    """Abstract FMI simple type definition.

    Args:
        name (str): Type name
        description (str, optional): Type description
    """

    def __init__(
            self,
            name: str,
            description: Optional[str] = None,
            getter: Any = None,
            setter: Any = None
    ):
        self.getter = getter
        self.setter = setter
        self.local_name = name.split(".")[-1]
        self.__attrs = {
            "name": name,
            "valueReference": None,
            "description": description,  # Only for ME
        }

    @property
    def name(self) -> str:
        """str: Type name"""
        return self.__attrs["name"]

    @property
    def description(self) -> Optional[str]:
        """str or None: Type description - None if not set"""
        return self.__attrs["description"]

    def to_xml(self) -> Element:
        """Convert the type to XML node.

        Returns
            xml.etree.ElementTree.Element: XML node
        """
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value)
        return Element("SimpleType", attrib)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class Real(SimpleType):
    def __init__(self, name: str, quantity: Optional[str] = None, unit: Optional[str] = None,
                 display_unit: Optional[str] = None, relative_quantity: Optional[bool] = None,
                 min_: Optional[float] = None, max_: Optional[float] = None, nominal: Optional[float] = None,
                 unbounded: Optional[bool] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {"quantity": quantity, "unit": unit, "displayUnit": display_unit,
                        "relativeQuantity": relative_quantity, "min": min_, "max": max_, "nominal": nominal,
                        "unbounded": unbounded}

    @property
    def quantity(self) -> Optional[str]:
        return self.__attrs["quantity"]

    @property
    def unit(self) -> Optional[str]:
        return self.__attrs["unit"]

    @property
    def display_unit(self) -> Optional[str]:
        return self.__attrs["displayUnit"]

    @property
    def relative_quantity(self) -> Optional[bool]:
        return self.__attrs["relativeQuantity"]

    @property
    def min(self) -> Optional[float]:
        return self.__attrs["min"]

    @property
    def max(self) -> Optional[float]:
        return self.__attrs["max"]

    @property
    def nominal(self) -> Optional[float]:
        return self.__attrs["nominal"]

    @property
    def unbounded(self) -> Optional[bool]:
        return self.__attrs["unbounded"]

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                # In order to not loose precision, a number of this type should be
                # stored on an XML file with at least 16 significant digits
                if key in ["min", "max", "nominal"]:
                    attrib[key] = f"{value:.16g}"
                elif key in ["relativeQuantity", "unbounded"]:
                    attrib[key] = str(value).lower()
                else:
                    attrib[key] = str(value)
        parent = super().to_xml()
        SubElement(parent, "Real", attrib)

        return parent


class Integer(SimpleType):
    def __init__(self, name: str, quantity: Optional[str] = None, min_: Optional[int] = None,
                 max_: Optional[int] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {"quantity": quantity, "min": min_, "max": max_}

    @property
    def quantity(self) -> Optional[str]:
        return self.__attrs["quantity"]

    @property
    def min(self) -> Optional[int]:
        return self.__attrs["min"]

    @property
    def max(self) -> Optional[int]:
        return self.__attrs["max"]

    def to_xml(self) -> Element:
        attrib = dict()
        for key, value in self.__attrs.items():
            if value is not None:
                attrib[key] = str(value)
        parent = super().to_xml()
        SubElement(parent, "Integer", attrib)

        return parent


class Item:
    def __init__(self, name: str, value: int, description: Optional[str] = None):
        self.name = name
        self.value = value
        self.description = description


class Enumeration(SimpleType):
    def __init__(self, name: str, item: list[Item], quantity: Optional[str] = None, **kwargs):
        super().__init__(name, **kwargs)
        self.__attrs = {"quantity": quantity, "Item": item}

    @property
    def quantity(self) -> Optional[str]:
        return self.__attrs["quantity"]

    @property
    def item(self) -> list[Item]:
        return self.__attrs["Item"]

    def to_xml(self) -> Element:
        attrib = dict()
        if self.quantity is not None:
            attrib["quantity"] = self.quantity
        parent = super().to_xml()
        sub = SubElement(parent, "Enumeration", attrib)

        for item in self.item:
            item_attrib = {"name": item.name, "value": str(item.value)}
            if item.description is not None:
                item_attrib["description"] = item.description
            SubElement(sub, "Item", item_attrib)

        return parent
