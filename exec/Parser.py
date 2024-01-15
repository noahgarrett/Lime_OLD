from exec.Lexer import Lexer
from models.Token import Token, TokenType
from typing import Callable

# AST Imports
from models.AST import Statement, Expression, Program, ExpressionStatement, PrefixExpression, InfixExpression, IntegerLiteral, FloatLiteral
from models.AST import IdentifierLiteral, LetStatement, BooleanLiteral, IfExpression, BlockStatement, AssignStatement, ReturnStatement
from models.AST import FunctionLiteral, CallExpression, StringLiteral, ArrayLiteral, HashLiteral, IndexExpression, ImportStatement, FromImportStatement
from models.AST import WhileStatement, ForStatement, FunctionStatement


# Precedence Types
P_LOWEST: int = 0
P_EQUALS: int = 1
P_LESSGREATER: int = 2
P_SUM: int = 3
P_PRODUCT: int = 4
P_EXPONENT: int = 5
P_PREFIX: int = 6
P_CALL: int = 7
P_INDEX: int = 8

# Precedence Mapping
PRECEDENCES: dict[TokenType, int] = {
    TokenType.PLUS: P_SUM,
    TokenType.MINUS: P_SUM,
    TokenType.SLASH: P_PRODUCT,
    TokenType.ASTERISK: P_PRODUCT,
    TokenType.MODULUS: P_PRODUCT,
    TokenType.POW: P_EXPONENT,
    TokenType.EQ: P_EQUALS,
    TokenType.NOT_EQ: P_EQUALS,
    TokenType.LT: P_LESSGREATER,
    TokenType.GT: P_LESSGREATER,
    TokenType.LT_EQ: P_LESSGREATER,
    TokenType.GT_EQ: P_LESSGREATER,
    TokenType.LPAREN: P_CALL,
    TokenType.LBRACKET: P_INDEX
}


class Parser:
    def __init__(self, lexer: Lexer, debug: bool = False) -> None:
        self.lexer: Lexer = lexer
        self.debug: bool = debug

        self.errors: list[str] = []

        self.current_token: Token = None
        self.peek_token: Token = None

        self.prefix_parse_fns: dict[TokenType, Callable] = {
            TokenType.IDENT: self.__parse_identifier,
            TokenType.INT: self.__parse_int_literal,
            TokenType.FLOAT: self.__parse_float_literal,
            TokenType.STRING: self.__parse_string_literal,
            TokenType.LPAREN: self.__parse_grouped_expression,
            TokenType.MINUS: self.__parse_prefix_expression,
            TokenType.BANG: self.__parse_prefix_expression,
            TokenType.TRUE: self.__parse_boolean,
            TokenType.FALSE: self.__parse_boolean,
            TokenType.IF: self.__parse_if_expression,
            TokenType.FUNCTION: self.__parse_function_literal,
            TokenType.LBRACKET: self.__parse_array_literal,
            TokenType.LBRACE: self.__parse_hash_literal
        }
        self.infix_parse_fns: dict[TokenType, Callable] = {
            TokenType.PLUS: self.__parse_infix_expression,
            TokenType.MINUS: self.__parse_infix_expression,
            TokenType.SLASH: self.__parse_infix_expression,
            TokenType.ASTERISK: self.__parse_infix_expression,
            TokenType.POW: self.__parse_infix_expression,
            TokenType.MODULUS: self.__parse_infix_expression,
            TokenType.EQ: self.__parse_infix_expression,
            TokenType.NOT_EQ: self.__parse_infix_expression,
            TokenType.LT: self.__parse_infix_expression,
            TokenType.GT: self.__parse_infix_expression,
            TokenType.LT_EQ: self.__parse_infix_expression,
            TokenType.GT_EQ: self.__parse_infix_expression,
            TokenType.LPAREN: self.__parse_call_expression,
            TokenType.LBRACKET: self.__parse_index_expression
        }

        # Populate the current_token and peek_token
        self.__next_token()
        self.__next_token()

    # region Parser Helpers
    def __next_token(self) -> None:
        self.current_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def __peek_error(self, tt: TokenType) -> None:
        self.errors.append(f"Expected next token to be {tt}, got {self.peek_token.type} instead.")
    
    def __current_token_is(self, tt: TokenType) -> bool:
        return self.current_token.type == tt

    def __peek_token_is(self, tt: TokenType) -> bool:
        return self.peek_token.type == tt
    
    def __expect_peek(self, tt: TokenType) -> bool:
        if self.__peek_token_is(tt):
            self.__next_token()
            return True
        else:
            self.__peek_error(tt)
            return False
        
    def __no_prefix_parse_fn_error(self, tt: TokenType):
        self.errors.append(f"No Prefix Parse Function for {tt} found")
    # endregion

    # region Precedence Helpers
    def __current_precedence(self) -> int:
        prec: int | None = PRECEDENCES.get(self.current_token.type)
        if prec is None:
            return P_LOWEST
        return prec
    
    def __peek_precedence(self) -> int:
        prec: int | None = PRECEDENCES.get(self.peek_token.type)
        if prec is None:
            return P_LOWEST
        return prec
    # endregion

    # region Parser Execution Methods
    def parse_program(self) -> Program:
        program: Program = Program()

        while self.current_token.type != TokenType.EOF:
            stmt: Statement = self.__parse_statement()
            if stmt is not None:
                program.statements.append(stmt)
            
            self.__next_token()
        
        return program
    # endregion

    # region Parser Execution **STATEMENT** methods
    def __parse_statement(self) -> Statement:
        if self.current_token.type == TokenType.IDENT and self.__peek_token_is(TokenType.ASSIGN):
            return self.__parse_assignment_statement()

        match self.current_token.type:
            case TokenType.LET:
                return self.__parse_let_statement()
            case TokenType.RETURN:
                return self.__parse_return_statement()
            case TokenType.IMPORT:
                return self.__parse_import_statement()
            case TokenType.FROM:
                return self.__parse_from_import_statement()
            case TokenType.WHILE:
                return self.__parse_while_statement()
            case TokenType.FOR:
                return self.__parse_for_statement()
            case TokenType.FUNCTION:
                return self.__parse_function_statement()
            case _:
                return self.__parse_expression_statement()
            
    def __parse_return_statement(self) -> ReturnStatement:
        stmt = ReturnStatement(token=self.current_token)

        self.__next_token()

        stmt.return_value = self.__parse_expression(P_LOWEST)

        if self.__peek_token_is(TokenType.SEMICOLON):
            self.__next_token()

        return stmt
    
    def __parse_expression_statement(self) -> ExpressionStatement:
        expr = self.__parse_expression(P_LOWEST)

        if self.__peek_token_is(TokenType.ASSIGN):
            self.__next_token()
            return self.__parse_assignment_statement(expr)

        if self.__peek_token_is(TokenType.SEMICOLON):
            self.__next_token()

        stmt: ExpressionStatement = ExpressionStatement(token=self.current_token, expr=expr)
        
        return stmt
    
    def __parse_assignment_statement(self, is_in_loop: bool = False) -> AssignStatement:
        stmt: AssignStatement = AssignStatement(token=self.current_token)

        stmt.ident = IdentifierLiteral(token=self.current_token, value=self.current_token.literal)

        self.__next_token()  # 'IDENT'
        self.__next_token()  # '='

        stmt.right_value = self.__parse_expression(P_LOWEST)
        
        if not is_in_loop:
            while not self.__current_token_is(TokenType.SEMICOLON) and not self.__current_token_is(TokenType.EOF):
                self.__next_token()
        
        return stmt
    
    def __parse_let_statement(self) -> LetStatement:
        stmt: LetStatement = LetStatement(token=self.current_token, name=None, value=None, value_type=None)

        if not self.__expect_peek(TokenType.IDENT):
            return None
        
        stmt.name = IdentifierLiteral(token=self.current_token, value=self.current_token.literal)

        # Type declaration additions
        if not self.__expect_peek(TokenType.COLON):
            return None
        
        
        if not self.__expect_peek(TokenType.TYPE):
            return None
        
        stmt.value_type = self.current_token.literal

        if not self.__expect_peek(TokenType.ASSIGN):
            return None
        
        self.__next_token()

        stmt.value = self.__parse_expression(P_LOWEST)

        if stmt.value.type() == "FunctionLiteral":
            stmt.value.name = stmt.name.value

        while not self.__current_token_is(TokenType.SEMICOLON) and not self.__current_token_is(TokenType.EOF):
            self.__next_token()
        
        return stmt
    
    def __parse_import_statement(self) -> ImportStatement:
        stmt: ImportStatement = ImportStatement(token=self.current_token)

        if not self.__expect_peek(TokenType.STRING):
            return None
        
        stmt.file_path = self.current_token.literal

        if not self.__expect_peek(TokenType.SEMICOLON):
            return None
        
        return stmt
    
    def __parse_from_import_statement(self) -> FromImportStatement:
        stmt: FromImportStatement = FromImportStatement(token=self.current_token)

        if not self.__expect_peek(TokenType.STRING):
            return None
        
        stmt.file_path = self.current_token.literal

        if not self.__expect_peek(TokenType.IMPORT):
            return None
        
        if not self.__expect_peek(TokenType.IDENT):
            return None
        
        stmt.imported_idents = [self.current_token]

        if not self.__expect_peek(TokenType.SEMICOLON):
            return None

        return stmt
    
    def __parse_while_statement(self) -> WhileStatement:
        stmt: WhileStatement = WhileStatement(token=self.current_token)

        self.__next_token()

        stmt.condition = self.__parse_expression(P_LOWEST)

        if not self.__expect_peek(TokenType.LBRACE):
            return None
        
        stmt.body = self.__parse_block_statement()

        return stmt
    
    def __parse_for_statement(self) -> ForStatement:
        stmt: ForStatement = ForStatement(token=self.current_token)

        if not self.__expect_peek(TokenType.LPAREN):
            return None
        
        self.__next_token()  # Skip the '('

        stmt.initializer = self.__parse_let_statement()

        if not self.__current_token_is(TokenType.SEMICOLON):
            return None
        
        self.__next_token()  # Skip the ';'

        stmt.condition = self.__parse_expression(P_LOWEST)

        if not self.__expect_peek(TokenType.SEMICOLON):
            return None
        
        self.__next_token()  # Skip the ';'

        stmt.increment = self.__parse_assignment_statement(is_in_loop=True)

        if not self.__expect_peek(TokenType.RPAREN):
            return None
        
        if not self.__expect_peek(TokenType.LBRACE):
            return None
        
        stmt.body = self.__parse_block_statement()

        return stmt
    
    def __parse_function_statement(self) -> FunctionStatement:
        stmt: FunctionStatement = FunctionStatement(token=self.current_token)

        if not self.__expect_peek(TokenType.IDENT):
            return None
        
        stmt.name = IdentifierLiteral(token=self.current_token, value=self.current_token.literal)

        if not self.__expect_peek(TokenType.LPAREN):
            return None

        stmt.parameters = self.__parse_function_parameters()

        if not self.__expect_peek(TokenType.ARROW):
            return None
        
        self.__next_token()

        stmt.return_type = self.current_token.literal

        if not self.__expect_peek(TokenType.LBRACE):
            return None
        
        stmt.body = self.__parse_block_statement()

        return stmt
        
    # endregion

    # region Parser Execution **EXPRESSION** methods
    def __parse_expression(self, precedence: int) -> Expression:
        prefix_fn: Callable | None = self.prefix_parse_fns.get(self.current_token.type) 
        if prefix_fn is None:
            self.__no_prefix_parse_fn_error(self.current_token.type)
            return None
        
        left_expr: Expression = prefix_fn()
        while not self.__peek_token_is(TokenType.SEMICOLON) and precedence < self.__peek_precedence():
            infix_fn: Callable | None = self.infix_parse_fns.get(self.peek_token.type)
            if infix_fn is None:
                return left_expr
            
            self.__next_token()

            left_expr = infix_fn(left_expr)

        return left_expr
    # endregion

    # region Prefix Methods
    def __parse_prefix_expression(self) -> Expression:
        prefix_expr: PrefixExpression = PrefixExpression(token=self.current_token, operator=self.current_token.literal)

        self.__next_token()

        prefix_expr.right_node = self.__parse_expression(P_PREFIX)

        return prefix_expr
    
    def __parse_int_literal(self) -> Expression:
        int_lit: IntegerLiteral = IntegerLiteral(token=self.current_token)

        try:
            int_lit.value = int(self.current_token.literal)
        except Exception as e:
            self.errors.append(f"Could not parse `{self.current_token.literal}` as integer")
            return None
        
        return int_lit
    
    def __parse_float_literal(self) -> Expression:
        float_lit: FloatLiteral = FloatLiteral(token=self.current_token)

        try:
            float_lit.value = float(self.current_token.literal)
        except Exception as e:
            self.errors.append(f"Could not parse `{self.current_token.literal}` as float")
            return None
        
        return float_lit
    
    def __parse_string_literal(self) -> Expression:
        return StringLiteral(token=self.current_token, value=self.current_token.literal)
    
    def __parse_grouped_expression(self) -> Expression:
        self.__next_token()

        expr: Expression = self.__parse_expression(P_LOWEST)

        if not self.__expect_peek(TokenType.RPAREN):
            return None
        
        return expr
    
    def __parse_identifier(self) -> Expression:
        return IdentifierLiteral(token=self.current_token, value=self.current_token.literal)
    
    def __parse_boolean(self) -> Expression:
        return BooleanLiteral(token=self.current_token, value=self.__current_token_is(TokenType.TRUE))
    
    def __parse_if_expression(self) -> Expression:
        condition = None
        consequence = None
        alternative = None

        self.__next_token()
        condition = self.__parse_expression(P_LOWEST)

        if not self.__expect_peek(TokenType.LBRACE):
            return None
        
        consequence = self.__parse_block_statement()

        if self.__peek_token_is(TokenType.ELSE):
            self.__next_token()

            if not self.__expect_peek(TokenType.LBRACE):
                return None
            
            alternative = self.__parse_block_statement()
        
        return IfExpression(token=self.current_token, condition=condition, consequence=consequence, alternative=alternative)
    
    def __parse_function_literal(self) -> Expression:
        lit: FunctionLiteral = FunctionLiteral(token=self.current_token)

        if not self.__expect_peek(TokenType.LPAREN):
            return None
        
        lit.parameters = self.__parse_function_parameters()

        if not self.__expect_peek(TokenType.LBRACE):
            return None
        
        lit.body = self.__parse_block_statement()

        return lit
    
    def __parse_array_literal(self) -> Expression:
        array: ArrayLiteral = ArrayLiteral(token=self.current_token)
        array.elements = self.__parse_expression_list(TokenType.RBRACKET)
        return array
    
    def __parse_hash_literal(self) -> Expression:
        h: HashLiteral = HashLiteral(token=self.current_token)
        
        while not self.__peek_token_is(TokenType.RBRACE):
            self.__next_token()
            key = self.__parse_expression(P_LOWEST)
            
            if not self.__expect_peek(TokenType.COLON):
                return None
            
            self.__next_token()
            value = self.__parse_expression(P_LOWEST)

            h.pairs[key] = value

            if not self.__peek_token_is(TokenType.RBRACE) and not self.__expect_peek(TokenType.COMMA):
                return None
        
        if not self.__expect_peek(TokenType.RBRACE):
            return None
        
        return h
    # endregion

    # region Prefix Helper Methods
    def __parse_block_statement(self) -> BlockStatement:
        block_stmt: BlockStatement = BlockStatement(token=self.current_token, statements=[])

        self.__next_token()

        while not self.__current_token_is(TokenType.RBRACE) and not self.__current_token_is(TokenType.EOF):
            stmt = self.__parse_statement()
            if stmt is not None:
                block_stmt.statements.append(stmt)
            
            self.__next_token()
        
        return block_stmt
    
    def __parse_function_parameters(self) -> list[IdentifierLiteral]:
        idents: list[IdentifierLiteral] = []

        if self.__peek_token_is(TokenType.RPAREN):
            self.__next_token()
            return idents
        
        self.__next_token()

        first_param: IdentifierLiteral = IdentifierLiteral(token=self.current_token, value=self.current_token.literal)

        if not self.__expect_peek(TokenType.COLON):
            return None
        
        self.__next_token()

        first_param.value_type = self.current_token.literal
        idents.append(first_param)

        while self.__peek_token_is(TokenType.COMMA):
            self.__next_token()
            self.__next_token()

            param: IdentifierLiteral = IdentifierLiteral(token=self.current_token, value=self.current_token.literal)
            
            if not self.__expect_peek(TokenType.COLON):
                return None
            
            self.__next_token()

            param.value_type = self.current_token.literal

            idents.append(param)
        
        if not self.__expect_peek(TokenType.RPAREN):
            return None
        
        return idents
    # endregion

    # region Infix Methods
    def __parse_infix_expression(self, left_node: Expression) -> Expression:
        infix_expr: InfixExpression = InfixExpression(token=self.current_token, operator=self.current_token.literal, left_node=left_node)

        precedence = self.__current_precedence()

        self.__next_token()

        infix_expr.right_node = self.__parse_expression(precedence)

        return infix_expr
    
    def __parse_call_expression(self, function: Expression) -> Expression:
        expr: CallExpression = CallExpression(token=self.current_token, function=function)
        expr.arguments = self.__parse_expression_list(TokenType.RPAREN)

        return expr
    
    def __parse_index_expression(self, left: Expression) -> Expression:
        expr: IndexExpression = IndexExpression(token=self.current_token, left=left)

        self.__next_token()
        expr.index = self.__parse_expression(P_LOWEST)

        if not self.__expect_peek(TokenType.RBRACKET):
            return None
        
        return expr
    # endregion

    # region Infix Helper Methods
    def __parse_expression_list(self, end: TokenType) -> list[Expression]:
        e_list: list[Expression] = []

        if self.__peek_token_is(end):
            self.__next_token()
            return e_list
        
        self.__next_token()
        e_list.append(self.__parse_expression(P_LOWEST))

        while self.__peek_token_is(TokenType.COMMA):
            self.__next_token()
            self.__next_token()

            e_list.append(self.__parse_expression(P_LOWEST))
        
        if not self.__expect_peek(end):
            return None
        
        return e_list
    # endregion