from models.AST import Program, Node, Expression, Statement
from models.AST import LetStatement, ExpressionStatement, BlockStatement, ReturnStatement, FunctionStatement, AssignStatement
from models.AST import WhileStatement, IfExpression, ImportStatement, FromImportStatement
from models.AST import InfixExpression, PrefixExpression, CallExpression
from models.AST import IntegerLiteral, IdentifierLiteral, FloatLiteral, StringLiteral, BooleanLiteral, FunctionLiteral

from llvmlite import ir
import os

from exec.Lexer import Lexer
from exec.Parser import Parser

class Compiler:
    def __init__(self) -> None:
        self.type_map: dict = {
            'bool': ir.IntType(1),
            'int': ir.IntType(32),
            'int64': ir.IntType(64),
            'float': ir.FloatType(),
            'double': ir.DoubleType(),
            'void': ir.VoidType(),
            'str': ir.ArrayType(ir.IntType(8), 1)  # String = array of chars (int8)
        }

        # Initializing the main module
        self.module: ir.Module = ir.Module('main')

        # Keeping track of defined variables
        self.variables: dict[str, tuple] = {}

        # Defining a builtin functions
        self.__initialize_builtins()

        # Current Builder
        self.builder: ir.IRBuilder = ir.IRBuilder()

        # Random counter for entries
        self.counter = -1
    
    def inc_counter(self) -> int:
        self.counter += 1
        return self.counter

    def compile(self, node: Node) -> None:
        match node.type():
            case "Program":
                self.__visit_program(node)
            
            # Statements
            case "LetStatement":
                self.__visit_let_statement(node)
            case "ExpressionStatement":
                self.__visit_expression_statement(node)
            case "BlockStatement":
                self.__visit_block_statement(node)
            case "ReturnStatement":
                self.__visit_return_statement(node)
            case "FunctionStatement":
                self.__visit_function_statement(node)
            case "AssignStatement":
                self.__visit_assign_statement(node)
            case "WhileStatement":
                self.__visit_while_statement(node)
            case "ImportStatement":
                self.__visit_import_statement(node)
            case "FromImportStatement":
                self.__visit_from_import_statement(node)

            # Expressions
            case "InfixExpression":
                self.__visit_infix_expression(node)
            case "CallExpression":
                self.__visit_call_expression(node)
            case "IfExpression":
                self.__visit_if_expression(node)

    def __initialize_builtins(self) -> ir.Function:
        def __init_print() -> ir.Function:
            fnty: ir.FunctionType = ir.FunctionType(
                self.type_map['int'],
                [ir.IntType(8).as_pointer()],
                var_arg=True
            )
            return ir.Function(self.module, fnty, 'printf')
        
        self.variables['printf'] = (__init_print(), ir.IntType(32))
    
    # region Visit Methods
    def __visit_program(self, node: Program) -> None:
        # Compile the body of the function / program
        for stmt in node.statements:
            self.compile(stmt)

    # Statements
    def __visit_import_statement(self, node: ImportStatement) -> None:
        file_path: str = node.file_path

        with open(os.path.abspath(file_path), "r") as f:
            code: str = f.read()

        l: Lexer = Lexer(source=code)
        p: Parser = Parser(lexer=l)

        program: Program = p.parse_program()
        if len(p.errors) > 0:
            print(f"Error with imported pallet: {file_path}")
            for err in p.errors:
                print(err)
            exit(1)
        
        self.compile(node=program)

    def __visit_from_import_statement(self, node: FromImportStatement) -> None:
        pass

    def __visit_let_statement(self, node: LetStatement) -> None:
        name: str = node.name.value
        value: Expression = node.value
        value_type: str = node.value_type

        value, Type = self.__resolve_value(node=value, value_type=value_type)

        if not self.variables.__contains__(name):
            # Creating a pointer for the type 'Type' : ir.Type
            ptr = self.builder.alloca(Type)

            # Storing the value to the pointer
            self.builder.store(value, ptr)

            # Adding the name and its pointer to the variables map
            self.variables[name] = ptr, Type
        else:
            ptr, _ = self.variables[name]
            self.builder.store(value, ptr)
    
    def __visit_expression_statement(self, node: ExpressionStatement) -> None:
        self.compile(node.expr)

    def __visit_block_statement(self, node: BlockStatement) -> None:
        for stmt in node.statements:
            self.compile(stmt)

    def __visit_return_statement(self, node: ReturnStatement) -> None:
        value = node.return_value
        value, Type = self.__resolve_value(value)
        self.builder.ret(value)

    def __visit_function_statement(self, node: FunctionStatement) -> None:
        name: str = node.name.value
        body: BlockStatement = node.body
        params: list[IdentifierLiteral] = node.parameters

        # Keep track of the names of each parameter
        param_names: list[str] = [p.value for p in params]

        # Keep track of the types for each parameter
        param_types: list[ir.Type] = [self.type_map[p.value_type] for p in params]

        # TODO: Function's return type (ALLOW MORE RETURN TYPES FROM FUNCTIONS, RN ITS JUST INTS)
        return_type: ir.Type = self.type_map[node.return_type]
        
        # Defining the function's (return_type, params_type)
        fnty = ir.FunctionType(return_type, param_types)
        func = ir.Function(self.module, fnty, name=name)

        # Define the function's block
        block = func.append_basic_block(f'{name}_entry')

        previous_builder = self.builder

        # Current builder
        self.builder = ir.IRBuilder(block)

        params_ptr = []

        # Storing the pointers of each param
        for i, typ in enumerate(param_types):
            ptr = self.builder.alloca(typ)
            self.builder.store(func.args[i], ptr)
            params_ptr.append(ptr)
        
        previous_variables = self.variables.copy()
        for i, x in enumerate(zip(param_types, param_names)):
            typ = param_types[i]
            ptr = params_ptr[i]

            # Add the function's parameter to the stored variables
            self.variables[x[1]] = ptr, typ
        
        # Adding the function to variables
        self.variables[name] = func, return_type

        # Compile the body of the function
        self.compile(body)

        # Removing the function's variables so it cannot be accessed by other functions
        self.variables = previous_variables
        self.variables[name] = func, return_type

        self.builder = previous_builder

    def __visit_assign_statement(self, node: AssignStatement) -> None:
        name: str = node.ident.value
        value = node.right_value

        value, Type = self.__resolve_value(value)

        if not self.variables.__contains__(name):
            ptr = self.builder.alloca(Type)
            
            self.builder.store(value, ptr)

            self.variables[name] = ptr, Type
        else:
            ptr, _ = self.variables[name]
            self.builder.store(value, ptr)

    def __visit_while_statement(self, node: WhileStatement) -> None:
        Test = node.condition
        body = node.body
        test, _ = self.__resolve_value(Test)

        # Entry (block that runs if the condition is true)
        while_loop_entry = self.builder.append_basic_block(f"while_loop_entry_{self.inc_counter()}")

        # If the condition is false, it runs from this block
        while_loop_otherwise = self.builder.append_basic_block(f"while_loop_otherwise_{self.counter}")

        # Creating a condition branch
        #     condition
        #        / \
        # if true   if false
        #       /   \
        #      /     \
        # true block  false block
        self.builder.cbranch(test, while_loop_entry, while_loop_otherwise)

        # Setting the builder position-at-start
        self.builder.position_at_start(while_loop_entry)
        
        self.compile(body)

        test, _ = self.__resolve_value(Test)

        self.builder.cbranch(test, while_loop_entry, while_loop_otherwise)
        self.builder.position_at_start(while_loop_otherwise)

    # Expressions
    def __visit_infix_expression(self, node: InfixExpression) -> tuple:
        operator: str = node.operator
        left_value, left_type = self.__resolve_value(node.left_node)
        right_value, right_type = self.__resolve_value(node.right_node)

        value = None
        Type = None
        if isinstance(right_type, ir.FloatType) and isinstance(left_type, ir.FloatType):
            Type = ir.FloatType()
            match operator:
                case '+':
                    value = self.builder.fadd(left_value, right_value)
                case '-':
                    value = self.builder.fsub(left_value, right_value)
                case '*':
                    value = self.builder.fmul(left_value, right_value)
                case '/':
                    value = self.builder.fdiv(left_value, right_value)
                case '<':
                    value = self.builder.fcmp_ordered('<', left_value, right_value)
                    Type = ir.IntType(1)
                case '<=':
                    value = self.builder.fcmp_ordered('<=', left_value, right_value)
                    Type = ir.IntType(1)
                case '>':
                    value = self.builder.fcmp_ordered('>', left_value, right_value)
                    Type = ir.IntType(1)
                case '>=':
                    value = self.builder.fcmp_ordered('>=', left_value, right_value)
                    Type = ir.IntType(1)
                case '==':
                    value = self.builder.fcmp_ordered('==', left_value, right_value)
                    Type = ir.IntType(1)
        elif isinstance(right_type, ir.IntType) and isinstance(left_type, ir.IntType):
            Type = ir.IntType(32)
            match operator:
                case '+':
                    value = self.builder.add(left_value, right_value)
                case '-':
                    value = self.builder.sub(left_value, right_value)
                case '*':
                    value = self.builder.mul(left_value, right_value)
                case '/':
                    value = self.builder.sdiv(left_value, right_value)
                case '<':
                    value = self.builder.icmp_signed('<', left_value, right_value)
                    Type = ir.IntType(1)
                case '==':
                    value = self.builder.icmp_signed('==', left_value, right_value)
                    Type = ir.IntType(1)
        
        return value, Type
    
    def __visit_prefix_expression(self, node: PrefixExpression) -> tuple:
        operator: str = node.operator
        right_node = node.right_node

        right_value, right_type = self.__resolve_value(right_node)

        Type = None
        value = None
        if isinstance(right_type, ir.FloatType):
            Type = ir.FloatType()
            match operator:
                case '-':
                    value = self.builder.fmul(right_value, ir.Constant(ir.FloatType(), -1.0))
        
        return value, Type
    
    def __visit_call_expression(self, node: CallExpression) -> tuple:
        name: str = node.function.value
        params: list[Expression] = node.arguments

        args = []
        types = []
        if len(params) > 0:
            for x in params:
                p_val, p_type = self.__resolve_value(x)
                args.append(p_val)
                types.append(p_type)

        # See if we are calling a built-in function or an user-defined function
        match name:
            case 'printf':
                ret = self.builtin_printf(params=args, return_type=types[0])
                ret_type = self.type_map['int']
            case _:
                func, ret_type = self.variables[name]
                ret = self.builder.call(func, args)
        
        return ret, ret_type
    
    def __visit_if_expression(self, node: IfExpression) -> None:
        condition = node.condition
        consequence = node.consequence
        alternative = node.alternative

        test, Type = self.__resolve_value(condition)

        # If there is no else block
        if alternative is None:
            with self.builder.if_then(test):
                # Runs this if true
                self.compile(consequence)
        else:
            with self.builder.if_else(test) as (true, otherwise):
                # Creating a condition branch
                #      condition
                #        / \
                #     true  false
                #       /   \
                #      /     \
                # if block  else block
                with true:
                    # Runs this if the condition is true
                    self.compile(consequence)

                with otherwise:
                    # Runs this if the condition is false
                    self.compile(alternative)
    # endregion
        
    # region Helper Methods
    def __resolve_value(self, node: Expression, value_type: str = None) -> tuple[ir.Value, ir.Type]:
        """ Resolves a value and returns a tuple (ir_value, ir_type) """
        match node.type():
            # Literal Values
            case "IntegerLiteral":
                node: IntegerLiteral = node
                value, Type = node.value, self.type_map['int' if value_type is None else value_type]
                return ir.Constant(Type, value), Type
            case "FloatLiteral":
                node: FloatLiteral = node
                value, Type = node.value, self.type_map['float' if value_type is None else value_type]
                return ir.Constant(Type, value), Type
            case "StringLiteral":
                node: StringLiteral = node
                string, Type = self.__convert_string(node.value)
                return string, Type
            case "IdentifierLiteral":
                node: IdentifierLiteral = node
                ptr, Type = self.variables[node.value]
                return self.builder.load(ptr), Type
            case "BooleanLiteral":
                node: BooleanLiteral = node
                value, Type = node.value, self.type_map['bool']
                return ir.Constant(Type, value), Type
            
            # Expression Values
            case "InfixExpression":
                return self.__visit_infix_expression(node)
            case "PrefixExpression":
                return self.__visit_prefix_expression(node)
            case "CallExpression":
                return self.__visit_call_expression(node)


    def __convert_string(self, string: str) -> tuple[ir.Constant, ir.ArrayType]:
        """ Strings are converted into an array of characters """
        # string = string[1:-1]
        string = string.replace('\\n', '\n\0')
        n = len(string) + 1
        buf = bytearray((' ' * n).encode('ascii'))
        buf[-1] = 0
        buf[:-1] = string.encode('utf8')
        return ir.Constant(ir.ArrayType(ir.IntType(8), n), buf), ir.ArrayType(ir.IntType(8), n)
    # endregion

    # region Builtin Functions
    def builtin_printf(self, params: list, return_type: ir.Type) -> None:
        """ Basic C builtin printf """

        format = params[0]
        params = params[1:]
        zero = ir.Constant(ir.IntType(32),0)
        ptr = self.builder.alloca(return_type)
        self.builder.store(format,ptr)
        format = ptr
        format = self.builder.gep(format, [zero, zero])
        format = self.builder.bitcast(format, ir.IntType(8).as_pointer())
        func,_ = self.variables['printf']
        return self.builder.call(func,[format,*params])
    # endregion
