from models.AST import IdentifierLiteral, Program, Expression, Statement, Node
from models.AST import LetStatement, ExpressionStatement, BlockStatement, ReturnStatement, FunctionStatement, AssignStatement
from models.AST import WhileStatement, IfExpression, ImportStatement, FromImportStatement, ClassStatement
from models.AST import InfixExpression, PrefixExpression, CallExpression
from models.AST import IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral

from models.Py_Template import AssignTemplate, CallTemplate, FunctionTemplate, IfTemplate, LetTemplate, WhileTemplate

from models.Environment import Environment

class Py_Compiler:
    def __init__(self) -> None:
        # List of import statements to append to the top of the outputed file
        self.import_statements: list[str] = [

        ]

        # Mapping from Lime types to Python types
        self.type_map: dict[str, str] = {
            'int': 'int',
            'void': 'None',
            'bool': 'bool',
            'str': 'str',
            'float': 'float',
        }

        # Keeping track of defined variables and their types
        self.env: Environment = Environment()

        # Initialize global functions / variables
        self.__initialize_builtins()

        self.tab_level: int = 0

    def compile(self, node: Program) -> str:
        match node.type():
            case "Program":
                return self.__visit_program(node)
            
            # Statements
            case "FunctionStatement":
                return self.__visit_function_statement(node)
            case "BlockStatement":
                return self.__visit_block_statement(node)
            case "ReturnStatement":
                return self.__visit_return_statement(node)
            case "ExpressionStatement":
                return self.__visit_expression_statement(node)
            case "LetStatement":
                return self.__visit_let_statement(node)
            case "WhileStatement":
                return self.__visit_while_statement(node)
            case "AssignStatement":
                return self.__visit_assign_statement(node)
            
            # Expressions
            case "IfExpression":
                return self.__visit_if_expression(node)
            case "InfixExpression":
                return self.__visit_infix_expression(node)
            case "CallExpression":
                return self.__visit_call_expression(node)

            # Literals
            case "IdentifierLiteral":
                return self.__visit_identifier_literal(node)
            case "IntegerLiteral":
                return self.__visit_integer_literal(node)
            case "FloatLiteral":
                return self.__visit_float_literal(node)
            case "StringLiteral":
                return self.__visit_string_literal(node)
            case "BooleanLiteral":
                return self.__visit_boolean_literal(node)
            
    def __initialize_builtins(self) -> None:
        """ Initialize the global functions / variables """
        self.env.define("print", None, None)
            
    # region VISIT HELPERS
    def __visit_program(self, node: Program) -> str:
        """ Entry point for compiling the AST """
        code: str = ""

        # Add the Program Body
        for stmt in node.statements:
            code += self.compile(stmt)

        # Add imports
        import_section: str = ""
        for _import in self.import_statements:
            import_section += f"import {_import}\n"

        # Combine everything into one file
        code = import_section + code + "main()"

        return code
            
    # region Statements
    def __visit_function_statement(self, node: FunctionStatement) -> str:
        name: str = node.name
        return_type: str = node.return_type
        params: list[IdentifierLiteral] = node.parameters
        body: BlockStatement = node.body

        previous_env: Environment = self.env

        self.env = Environment(parent=previous_env, name=f"{name}_scope")

        func_template: FunctionTemplate = FunctionTemplate(
            tab_level=self.tab_level,
            name=self.compile(name),
            params=','.join([self.compile(param) for param in params]),
            return_type=self.type_map[return_type]
        )

        # Add the function body
        self.tab_level += 1
        func_template.body = self.compile(body)
        self.tab_level -= 1

        self.env = previous_env
        self.env.define(name, None ,return_type)

        return func_template.get_template()

    def __visit_block_statement(self, node: BlockStatement) -> str:
        code: str = ""
        for stmt in node.statements:
            code += self.compile(stmt)

        return code
    
    def __visit_return_statement(self, node: ReturnStatement) -> str:
        return self.__add_tab_level(f"return {self.compile(node.return_value)}\n")
    
    def __visit_expression_statement(self, node: ExpressionStatement) -> str:
        return f"{self.compile(node.expr)}\n"
    
    def __visit_let_statement(self, node: LetStatement) -> str:
        name: str = self.compile(node.name)
        value: str = self.compile(node.value)
        value_type: str = node.value_type

        let_template: LetTemplate = LetTemplate(
            tab_level=self.tab_level,
            name=name,
            value=value,
            value_type=value_type
        )

        self.env.define(name, value, value_type)

        return let_template.get_template()
    
    def __visit_while_statement(self, node: WhileStatement) -> str:
        condition: str = self.compile(node.condition)
        
        self.tab_level += 1
        body: str = self.compile(node.body)
        self.tab_level -= 1

        while_template: WhileTemplate = WhileTemplate(
            tab_level=self.tab_level,
            condition=condition,
            body=body
        )

        return while_template.get_template()
    
    def __visit_assign_statement(self, node: AssignStatement) -> str:
        identifier: str = self.compile(node.ident)
        value: str = self.compile(node.right_value)

        assign_template: AssignTemplate = AssignTemplate(
            tab_level=self.tab_level,
            identifier=identifier,
            value=value
        )

        return assign_template.get_template()
    # endregion
            
    # region Expressions
    def __visit_if_expression(self, node: IfExpression) -> str:
        condition: str = self.compile(node.condition)

        self.tab_level += 1
        consequence = self.compile(node.consequence)
        self.tab_level -= 1

        self.tab_level += 1
        alternative: str = self.compile(node.alternative) if node.alternative else None
        self.tab_level -= 1

        if_template: IfTemplate = IfTemplate(
            tab_level=self.tab_level,
            condition=condition,
            consequence=consequence,
            alternative=alternative
        )

        return if_template.get_template()


    def __visit_infix_expression(self, node: InfixExpression) -> str:
        left_grouping: bool = True if node.left_node.type() == "InfixExpression" else False
        right_grouping: bool = True if node.right_node.type() == "InfixExpression" else False

        left_node: Expression = self.compile(node.left_node)
        opertator: str = node.operator
        right_node: Expression = self.compile(node.right_node)

        left_str: str = f"({left_node})" if left_grouping else left_node
        right_str: str = f"({right_node})" if right_grouping else right_node

        return f"{left_str} {opertator} {right_str}"
    
    def __visit_call_expression(self, node: CallExpression) -> str:
        function_name: str = self.compile(node.function)
        arguments: str = ",".join([self.compile(arg) for arg in node.arguments])

        call_template: CallTemplate = CallTemplate(
            tab_level=self.tab_level,
            name=function_name,
            arguments=arguments
        )

        return call_template.get_template()
    # endregion
            
    # region Literals
    def __visit_identifier_literal(self, node: IdentifierLiteral) -> str:
        return node.value
    
    def __visit_integer_literal(self, node: IntegerLiteral) -> str:
        return str(node.value)
    
    def __visit_float_literal(self, node: FloatLiteral) -> str:
        return str(node.value)
    
    def __visit_boolean_literal(self, node: BooleanLiteral) -> str:
        return 'True' if node.value else 'False'
    
    def __visit_string_literal(self, node: StringLiteral) -> str:
        return f'"{node.value}"'
    # endregion

    # endregion

    # region Helpers
    def __add_tab_level(self, code: str) -> str:
        return ("\t" * self.tab_level) + code
    # endregion
