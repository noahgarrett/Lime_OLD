

class Environment:
    def __init__(self, records: dict[str, str] = None, parent = None, name: str = "global") -> None:
        self.records: dict[str, tuple] = records if records else {}
        self.parent: Environment = parent
        self.name: str = name

    def define(self, name: str, value: str, _type: str) -> str:
        self.records[name] = (value, _type)
        return value
    
    def lookup(self, name: str) -> str:
        return self.__resolve(name)
    
    def __resolve(self, name: str) -> str:
        if name in self.records:
            return self.records[name]
        elif self.parent:
            return self.parent.__resolve(name)
        else:
            raise RuntimeError(f"Undefined variable '{name}' in `{self.name}`'s scope.")
