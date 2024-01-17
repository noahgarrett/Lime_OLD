from models.AST import Program, Expression, Statement, Node
from models.AST import LetStatement, ExpressionStatement, BlockStatement, ReturnStatement, FunctionStatement, AssignStatement
from models.AST import WhileStatement, IfExpression, ImportStatement, FromImportStatement, ClassStatement, IdentifierLiteral
from models.AST import InfixExpression, PrefixExpression, CallExpression, IntegerLiteral, FloatLiteral, StringLiteral, BooleanLiteral, FunctionLiteral

class C_Compiler:
    def __init__(self) -> None:
        # Holds the entire file's source code
        self.code: str = ""
        
        # List of include statements to append to the top of the outputed file
        self.include_statements: list[str] = [
            "<stdbool.h>",
            "<stdlib.h>"
        ]

        # List of typedefs to set at the top of the file
        self.typedefs: list[str] = [
            
        ]

        # Mapping from Lime types to C types
        self.type_map: dict[str, str] = {
            'int': 'int',
            'void': 'void',
            'bool': 'bool',
            'str': 'char'
        }

        # Keeping track of defined variables and their types
        self.variables: dict[str, str] = {}

        # Keeping track of variables to free when leaving scope
        self.free_variables: list[str] = []

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
            case "LetStatement":
                return self.__visit_let_statement(node)
            case "AssignStatement":
                return self.__visit_assign_statement(node)
            
            # Expressions

            # Literals
            case "IdentifierLiteral":
                return self.__visit_identifier_literal(node)
            case "FloatLiteral":
                return self.__visit_float_literal(node)
            case "IntegerLiteral":
                return self.__visit_integer_literal(node)
            case "BooleanLiteral":
                return self.__visit_boolean_literal(node)
            case "StringLiteral":
                return self.__visit_string_literal(node)

    # region VISIT METHODS
    def __visit_program(self, node: Program) -> str:
        """ Entry point to compiling the AST """
        code: str = ""

        # Add Program Body
        for stmt in node.statements:
            code += self.compile(stmt)

        # Add includes
        include_section: str = ""
        for include in self.include_statements:
            include_section += f"#include {include}\n"

        # Add typedefs
        typedef_section: str = ""
        for typedef in self.typedefs:
            typedef_section += f"{typedef}\n"

        code = include_section + typedef_section + code
        
        return code

    # region Statements
    def __visit_function_statement(self, node: FunctionStatement) -> str:
        name: str = self.compile(node.name)
        return_type: str = node.return_type
        params: list[IdentifierLiteral] = node.parameters
        body: BlockStatement = node.body

        previous_scope: dict[str, str] = self.variables.copy()

        self.variables = {}

        func_template: str = "{return_type} {name}({params}) { {body} }"

        # Populate the template
        func_template = func_template.replace('{return_type}', self.type_map[return_type])
        func_template = func_template.replace('{name}', name)
        func_template = func_template.replace('{params}', ','.join([self.compile(p) for p in params]))
        func_template = func_template.replace('{body}', self.compile(body))

        # Reset the variables back to parent scope with the newly added function
        self.variables = previous_scope
        self.variables[name] = return_type

        return func_template

    def __visit_block_statement(self, node: BlockStatement) -> str:
        code: str = ""
        for stmt in node.statements:
            code += self.compile(stmt)

        # Free the variables
        for var in self.free_variables:
            code += f"free({var});"

        self.free_variables = []

        return code

    def __visit_return_statement(self, node: ReturnStatement) -> str:
        return f"return {self.compile(node.return_value)};"
    
    def __visit_let_statement(self, node: LetStatement) -> str:
        name: str = node.name.value
        value: Expression = self.compile(node.value)
        value_type: str = node.value_type

        self.variables[name] = value_type
        self.free_variables.append(name)

        let_template: str = "{type} {possible_ptr_addr}{name}{possible_array} = {value};"

        let_template = let_template.replace('{type}', self.type_map[value_type])
        let_template = let_template.replace('{name}', name)
        let_template = let_template.replace('{possible_array}', '')

        # Populate the template
        if value_type == 'str':
            let_template = let_template.replace('{possible_ptr_addr}', '*')
            let_template = let_template.replace('{value}', f'strdup({value})')
        else:
            let_template = let_template.replace('{value}', value)

        return let_template

    def __visit_assign_statement(self, node: AssignStatement) -> str:
        ident_name: str = self.compile(node.ident)
        value = self.compile(node.right_value)

        assign_template: str = "{ident_name} = {value};"

        # Populate the template
        if self.variables[ident_name] == 'str':
            self.__include_lib('string')
            return f"strcpy({ident_name}, {value});"

        assign_template = assign_template.replace('{ident_name}', ident_name)
        assign_template = assign_template.replace('{value}', value)

        return assign_template
    # endregion

    # region Expressions

    # endregion

    # region Literals
    def __visit_identifier_literal(self, node: IdentifierLiteral) -> str:
        return node.value
    
    def __visit_integer_literal(self, node: IntegerLiteral) -> str:
        return str(node.value)
    
    def __visit_float_literal(self, node: FloatLiteral) -> str:
        return str(node.value)
    
    def __visit_boolean_literal(self, node: BooleanLiteral) -> str:
        return 'true' if node.value else 'false'
    
    def __visit_string_literal(self, node: StringLiteral) -> str:
        return f'"{node.value}"'
    # endregion

    # endregion

    # region Include Helpers
    def __include_lib(self, lib: str) -> str:
        if f"<{lib}.h>" not in self.include_statements:
            self.include_statements.append(f'<{lib}.h>')
    # endregion