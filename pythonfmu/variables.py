from abc import ABC, abstractmethod

from .enums import Fmi2Causality, Fmi2Initial, Fmi2Variability


class ScalarVariable(ABC):

    __vr_counter = 0

    def __init__(self, name):
        self.name = name
        self.initial = None
        self.causality = None
        self.variability = None
        self.description = None
        self.value_reference = ScalarVariable.__get_and_increment_vr()

    @staticmethod
    def __get_and_increment_vr():
        vr = ScalarVariable.__vr_counter
        ScalarVariable.__vr_counter += 1
        return vr

    def set_description(self, description: str):
        self.description = description
        return self

    def set_initial(self, initial: Fmi2Initial):
        self.initial = initial
        return self

    def set_causality(self, causality: Fmi2Causality):
        self.causality = causality
        return self

    def set_variability(self, variability: Fmi2Variability):
        self.variability = variability
        return self

    def __xml_repr__(self):
        xml_repr = f'\t\t<ScalarVariable valueReference="{self.value_reference}" name="{self.name}"'
        if self.initial is not None:
            xml_repr += f' initial="{self.initial.name}"'
        if self.causality is not None:
            xml_repr += f' causality="{self.causality.name}"'
        if self.variability is not None:
            xml_repr += f' variability="{self.variability.name}"'
        if self.description is not None:
            xml_repr += f' description="{self.description}"'
        xml_repr += ">\n"
        xml_repr += "\t\t\t" + self.__sub_xml_repr__() + "\n"
        return xml_repr + "\t\t</ScalarVariable>"

    @abstractmethod
    def __sub_xml_repr__(self):
        pass


class Real(ScalarVariable):
    def __init__(self, name):
        super().__init__(name)

    def __sub_xml_repr__(self):
        return f"<Real />"


class Integer(ScalarVariable):
    def __init__(self, name):
        super().__init__(name)

    def __sub_xml_repr__(self):
        return f"<Integer />"


class Boolean(ScalarVariable):
    def __init__(self, name):
        self.value = False
        super().__init__(name)

    def __sub_xml_repr__(self):
        return f"<Boolean />"


class String(ScalarVariable):
    def __init__(self, name):
        super().__init__(name)

    def __sub_xml_repr__(self):
        return f"<String />"
