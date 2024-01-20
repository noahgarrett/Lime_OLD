from abc import ABC, abstractmethod
from models.Token import Token

class Node(ABC):
    @abstractmethod
    def token_literal(self) -> str:
        pass

    @abstractmethod
    def string(self) -> str:
        pass

    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def json(self) -> dict:
        pass


class Statement(Node):
    pass

class Expression(Node):
    pass

class Program(Node):
    def __init__(self) -> None:
        self.statements: list[Statement] = []

        self.exports: list[Statement] = []
    
    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ""
        
    def string(self) -> str:
        output: str = ""
        for s in self.statements:
            output += f"{s.string()}\n"
        
        return output
    
    def type(self) -> str:
        return "Program"
    
    def json(self) -> dict:
        return {
            "statements": [{stmt.type(): stmt.json()} for stmt in self.statements],
            "exports": [{stmt.type(): stmt.json()} for stmt in self.exports]
        }
    

# region Statements
class ExpressionStatement(Statement):
    def __init__(self, token: Token, expr: Expression = None) -> None:
        self.token: Token = token
        self.expr: Expression = expr

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        if self.expr is not None:
            return self.expr.string()
        
        return ""
    
    def type(self) -> str:
        return "ExpressionStatement"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "expr": self.expr.json()
        }
    
class AssignStatement(Statement):
    def __init__(self, token: Token, ident = None, right_value: Expression = None) -> None:
        self.token = token
        self.ident: IdentifierLiteral = ident
        self.right_value: Expression = right_value
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return f"{self.ident.string()} = {self.right_value.string()};"
    
    def type(self) -> str:
        return "AssignStatement"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "identifier": self.ident.json(),
            "value": self.right_value.json()
        }
    
class LetStatement(Statement):
    def __init__(self, token: Token, name, value: Expression, value_type: str) -> None:
        self.token = token
        self.name: IdentifierLiteral = name
        self.value = value

        self.value_type: str = value_type

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += f"{self.token_literal()} "
        output += self.name.string()
        output += " = "

        if self.value is not None:
            output += self.value.string()
        
        output += ";"

        return output
    
    def type(self) -> str:
        return "LetStatement"
    
    def json(self) -> dict:
        return {
            "type": "LetStatement",
            "name": self.name.json(),
            "value": self.value.json(),
            "value_type": self.value_type
        }
    
class ClassStatement(Statement):
    def __init__(self, token: Token, name: str = None, body = None) -> None:
        self.token = token
        self.name: str = name
        self.body: BlockStatement = [] if body is None else body

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return f"<Class {self.file_path}>"

    def type(self) -> str:
        return "ClassStatement"
    
    def json(self) -> dict:
        return {
            "token": self.token.literal,
            "name": self.name,
            "body": self.body.json()
        }
    
class ImportStatement(Statement):
    def __init__(self, token: Token, file_path: str = None) -> None:
        self.token = token
        self.file_path = file_path

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return f"<Import {self.file_path}>"

    def type(self) -> str:
        return "ImportStatement"
    
    def json(self) -> dict:
        return {
            "token": self.token.literal,
            "file_path": self.file_path
        }
    
class FromImportStatement(Statement):
    def __init__(self, token: Token, file_path: str = None, imported_idents: list = None) -> None:
        self.token = token
        self.file_path = file_path
        self.imported_idents: list[IdentifierLiteral] = [] if imported_idents is None else imported_idents

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return f"<FromImport {self.file_path}>"

    def type(self) -> str:
        return "FromImportStatement"
    
    def json(self) -> dict:
        return {
            "token": self.token.literal,
            "file_path": self.file_path,
            "imported_idents": [ident.json() for ident in self.imported_idents]
        }
    
class BlockStatement(Statement):
    def __init__(self, token: Token, statements: list[Statement] = None) -> None:
        self.token = token
        self.statements = statements if statements is not None else []

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        for stmt in self.statements:
            output += stmt.string()
        
        return output
    
    def type(self) -> str:
        return "BlockStatement"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "statements": [stmt.json() for stmt in self.statements]
        }
    
class ReturnStatement(Statement):
    def __init__(self, token: Token, return_value: Expression = None) -> None:
        self.token = token
        self.return_value = return_value
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += f"{self.token_literal()} "

        if self.return_value is not None:
            output += self.return_value.string()

        output += ";"
        return output
    
    def type(self) -> str:
        return "ReturnStatement"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "return_value": self.return_value.json()
        }
    
class WhileStatement(Statement):
    def __init__(self, token: Token, condition: Expression = None, body: BlockStatement = None) -> None:
        self.token = token
        self.condition = condition
        self.body = body

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "while "
        output += self.condition.string()
        output += " "
        output += self.body.string()

        return output
    
    def type(self) -> str:
        return "WhileStatement"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "condition": self.condition.json(),
            "body": self.body.json()
        }
    
class ForStatement(Statement):
    def __init__(self, token: Token, initializer: LetStatement = None, condition: Expression = None, increment: Expression = None, body: BlockStatement = None) -> None:
        self.token = token
        self.initializer = initializer
        self.condition = condition
        self.increment = increment
        self.body = body

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "for "
        output += f"({self.initializer.string()}; "
        output += f"{self.condition.string()}; "
        output += f"{self.increment.string()})"
        output += "{ "
        output += self.body.string()
        output += " }"

        return output
    
    def type(self) -> str:
        return "ForStatement"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "initializer": self.initializer.json(),
            "condition": self.condition.json(),
            "increment": self.increment.json(),
            "body": self.body.json()
        }
    
class FunctionStatement(Statement):
    def __init__(self, token: Token, parameters: list = [], body: BlockStatement = None, name = None, return_type: str = None) -> None:
        self.token = token
        self.parameters = parameters
        self.body = body
        self.name = name

        self.return_type = return_type
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        params: list[str] = []
        for p in self.parameters:
            params.append(p.string())
        
        output += self.token_literal()
        if not self.name == "":
            output += f"<{self.name}>"
        output += "("
        output += ",".join(params)
        output += ") "
        output += "{ "
        output += self.body.string()
        output += " }"
        
        return output
    
    def type(self) -> str:
        return "FunctionStatement"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "name": self.name.json(),
            "return_type": self.return_type,
            "parameters": [p.json() for p in self.parameters],
            "body": self.body.json()
        }

# endregion

# region Expressions
class PrefixExpression(Expression):
    def __init__(self, token: Token, operator: str, right_node: Expression = None) -> None:
        self.token: Token = token  # The prefix token ('!' or '-')
        self.operator: str = operator
        self.right_node: Expression = right_node

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "("
        output += self.operator
        output += self.right_node.string()
        output += ")"

        return output
    
    def type(self) -> str:
        return "PrefixExpression"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "prefix_token": str(self.token),
            "operator": self.operator,
            "right_node": self.right_node.json()
        }

class InfixExpression(Expression):
    def __init__(self, token: Token, left_node: Expression, operator: str, right_node: Expression = None) -> None:
        self.token: Token = token
        self.left_node: Expression = left_node
        self.operator: str = operator
        self.right_node: Expression = right_node

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "("
        output += self.left_node.string()
        output += f" {self.operator} "
        output += self.right_node.string()
        output += ")"

        return output
    
    def type(self) -> str:
        return "InfixExpression"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "left_node": self.left_node.json(),
            "operator": self.operator,
            "right_node": self.right_node.json()
        }
    
class IfExpression(Expression):
    def __init__(self, token: Token, condition: Expression = None, consequence: BlockStatement = None, alternative: BlockStatement = None) -> None:
        self.token = token
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "if"
        output += self.condition.string()
        output += " "
        output += self.consequence.string()

        if self.alternative is not None:
            output += "else "
            output += self.alternative.string()
        
        return output
    
    def type(self) -> str:
        return "IfExpression"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "condition": self.condition.json(),
            "consequence": self.consequence.json(),
            "alternative": self.alternative.json() if self.alternative is not None else None
        }
    
class CallExpression(Expression):
    def __init__(self, token: Token, function: Expression = None, arguments: list[Expression] = None) -> None:
        self.token = token
        self.function = function
        self.arguments = arguments
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        args: list[str] = []
        for a in self.arguments:
            args.append(a.string())
        
        output += self.function.string()
        output += "("
        output += ",".join(args)
        output += ")"

        return output
    
    def type(self) -> str:
        return "CallExpression"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "function": self.function.json(),
            "arguments": [arg.json() for arg in self.arguments]
        }
    
class IndexExpression(Expression):
    def __init__(self, token: Token, left: Expression = None, index: Expression = None) -> None:
        self.token = token
        self.left = left
        self.index = index

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        output += "("
        output += self.left.string()
        output += "["
        output += self.index.string()
        output += "])"
        return output
    
    def type(self) -> str:
        return "IndexExpression"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "left_node": self.left.json(),
            "index_node": self.index.json()
        }
# endregion

# region Literals
class IntegerLiteral(Expression):
    def __init__(self, token: Token, value: int = None) -> None:
        self.token: Token = token
        self.value: int = value

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return self.token.literal
    
    def type(self) -> str:
        return "IntegerLiteral"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "value": self.value
        }
    
class FloatLiteral(Expression):
    def __init__(self, token: Token, value: float = None) -> None:
        self.token: Token = token
        self.value: float = value

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return self.token.literal
    
    def type(self) -> str:
        return "FloatLiteral"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "value": self.value
        }
    
class StringLiteral(Expression):
    def __init__(self, token: Token, value: str = None) -> None:
        self.token = token
        self.value = value
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return self.token.literal
    
    def type(self) -> str:
        return "StringLiteral"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "value": self.value
        }
    
class IdentifierLiteral(Expression):
    def __init__(self, token: Token, value: str = None) -> None:
        self.token = token
        self.value = value

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return self.value
    
    def type(self) -> str:
        return "IdentifierLiteral"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "value": self.value
        }
    
class BooleanLiteral(Expression):
    def __init__(self, token: Token, value: bool = False) -> None:
        self.token = token
        self.value = value
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        return self.token.literal
    
    def type(self) -> str:
        return "BooleanLiteral"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "value": self.value
        }
    
class ArrayLiteral(Expression):
    def __init__(self, token: Token, elements: list[Expression] = None) -> None:
        self.token = token
        self.elements: list[Expression] = [] if elements is None else elements

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        elements: list[str] = [el.string() for el in self.elements]

        output += "["
        output += ",".join(elements)
        output += "]"
        return output

    def type(self) -> str:
        return "ArrayLiteral"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "elements": [e.json() for e in self.elements]
        }
    
class HashLiteral(Expression):
    def __init__(self, token: Token, pairs: dict[Expression, Expression] = None) -> None:
        self.token = token
        self.pairs = {} if pairs is None else pairs
    
    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        pairs: list[str] = []
        for key, value in self.pairs.items():
            pairs.append(f"{key.string()}: {value.string()}")
        
        output += "{"
        output += ", ".join(pairs)
        output += "}"
        return output
    
    def type(self) -> str:
        return "HashLiteral"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "pairs": [{"key": key.json(), "value": value.json()} for key, value in self.pairs.items()]
        }
    
class FunctionLiteral(Expression):
    def __init__(self, token: Token, parameters: list[IdentifierLiteral] = None, body: BlockStatement = None, name: str = "", return_type: str = None) -> None:
        self.token = token
        self.parameters = parameters
        self.body = body
        self.name: str = name

        self.return_type: str = return_type

    def token_literal(self) -> str:
        return self.token.literal
    
    def string(self) -> str:
        output: str = ""

        params: list[str] = []
        for p in self.parameters:
            params.append(p.string())
        
        output += self.token_literal()
        if not self.name == "":
            output += f"<{self.name}>"
        output += "("
        output += ",".join(params)
        output += ") "
        output += "{ "
        output += self.body.string()
        output += " }"
        
        return output
    
    def type(self) -> str:
        return "FunctionLiteral"
    
    def json(self) -> dict:
        return {
            "type": self.type(),
            "name": self.name,
            "parameters": [p.json() for p in self.parameters],
            "return_type": self.return_type,
            "body": self.body.json()
        }
# endregion