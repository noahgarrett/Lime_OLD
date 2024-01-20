from abc import ABC, abstractmethod

class Template(ABC):
    @abstractmethod
    def get_template(self) -> str:
        """ Returns the fully populated string template for this class """
        pass

class FunctionTemplate(Template):
    def __init__(self, tab_level: int, name: str, params: str, return_type: str, body: str = None) -> None:
        self.tab_level = tab_level
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body

        self.__template: str = "def {name}({params}) -> {return_type}:\n{body}\n"

    def get_template(self) -> str:
        # Populate the template
        template = self.__template.replace('{name}', self.name) \
                            .replace('{params}', self.params) \
                            .replace('{return_type}', self.return_type) \
                            .replace('{body}', self.body)

        return ("\t" * self.tab_level) + template
    
class IfTemplate(Template):
    def __init__(self, tab_level: int, condition: str, consequence: str, alternative: str = None) -> None:
        self.tab_level = tab_level
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

        self.__template: str = "if {condition}:\n{consequence}"
        self.__else_template: str = "else:\n{alternative}"

    def get_template(self) -> str:
        # Populate the template
        template = self.__template.replace('{condition}', self.condition) \
                            .replace('{consequence}', self.consequence) \
        
        if self.alternative:
            else_temp: str = ("\t" * self.tab_level) + self.__else_template
            template += else_temp.replace('{alternative}', self.alternative)
        
        return ("\t" * self.tab_level) + template
    
class LetTemplate(Template):
    def __init__(self, tab_level: int, name: str, value: str, value_type: str) -> None:
        self.tab_level = tab_level
        self.name = name
        self.value = value
        self.value_type = value_type

        self.__template: str = "{name}: {value_type} = {value}\n"

    def get_template(self) -> str:
        # Populate the template
        template = self.__template.replace('{name}', self.name) \
                                    .replace('{value}', self.value) \
                                    .replace('{value_type}', self.value_type)
        
        return ("\t" * self.tab_level) + template
    
class CallTemplate(Template):
    def __init__(self, tab_level: int, name: str, arguments: str) -> None:
        self.tab_level = tab_level
        self.name = name
        self.arguments = arguments

        self.__template: str = "{name}({arguments})"

    def get_template(self) -> str:
        # Populate the template
        template = self.__template.replace('{name}', self.name) \
                                    .replace('{arguments}', self.arguments)
        
        return ("\t" * self.tab_level) + template
    
class WhileTemplate(Template):
    def __init__(self, tab_level: int, condition: str, body: str) -> None:
        self.tab_level = tab_level
        self.condition = condition
        self.body = body

        self.__template: str = "while {condition}:\n{body}"

    def get_template(self) -> str:
        # Populate the template
        template = self.__template.replace('{condition}', self.condition).replace('{body}', self.body)

        return ("\t" * self.tab_level) + template
    
class ForTemplate(Template):
    def __init__(self, tab_level: int, initializer_name: str, initializer_value: str, condition: str, increment: str, body: str) -> None:
        self.tab_level = tab_level
        self.initializer_name = initializer_name
        self.initializer_value = initializer_value
        self.condition = condition
        self.increment = increment
        self.body = body

        self.__template: str = "for {initializer_name} in range({initializer_value}, {condition}, {increment}):\n{body}"

    def get_template(self) -> str:
        # Populate the template
        template = self.__template.replace('{initializer_name}', self.initializer_name) \
                                    .replace('{initializer_value}', self.initializer_value) \
                                    .replace('{condition}', self.condition) \
                                    .replace('{increment}', self.increment)
        
        return ("\t" * self.tab_level) + template
    
class AssignTemplate(Template):
    def __init__(self, tab_level: int, identifier: str, value: str) -> None:
        self.tab_level = tab_level
        self.identifier = identifier
        self.value = value

        self.__template: str = "{identifier} = {value}"

    def get_template(self) -> str:
        # Populate the template
        template = self.__template.replace('{identifier}', self.identifier).replace('{value}', self.value)

        return ("\t" * self.tab_level) + template
