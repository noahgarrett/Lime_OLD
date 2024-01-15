from models.Token import Token, TokenType, lookup_ident


class Lexer:
    def __init__(self, source: str, debug: bool = False) -> None:
        self.source: str = source
        self.position: int = -1
        self.read_position: int = 0
        self.current_char: str = None
        
        self.debug: bool = debug

        self.__read_char()

    # region Lexer Helper Methods
    def __read_char(self) -> None:
        """ Reads the next char in the source input file """
        if self.read_position >= len(self.source):
            self.current_char = None
        else:
            self.current_char = self.source[self.read_position]
        
        self.position = self.read_position
        self.read_position += 1

    def __peek_char(self) -> str | None:
        """ Peeks to the upcoming char without advancing the lexer position """
        if self.read_position >= len(self.source):
            return None
        else:
            return self.source[self.read_position]
    # endregion

    # region Lexer Execution Method
    def next_token(self) -> Token:
        tok: Token = None

        self.__skip_whitespace()

        # Skip Comments
        # if self.current_char == '/' and self.__peek_char() == '/':
        #     self.__skip_comment()

        match self.current_char:
            case '+':
                tok = self.__new_token(TokenType.PLUS, self.current_char)
            case '-':
                # Handle '->'
                if self.__peek_char() == '>':
                    ch = self.current_char
                    self.__read_char()
                    tok = self.__new_token(TokenType.ARROW, ch + self.current_char)
                else:
                    tok = self.__new_token(TokenType.MINUS, self.current_char)
            case '*':
                tok = self.__new_token(TokenType.ASTERISK, self.current_char)
            case '/':
                tok = self.__new_token(TokenType.SLASH, self.current_char)
            case '%':
                tok = self.__new_token(TokenType.MODULUS, self.current_char)
            case '^':
                tok = self.__new_token(TokenType.POW, self.current_char)
            case '(':
                tok = self.__new_token(TokenType.LPAREN, self.current_char)
            case ')':
                tok = self.__new_token(TokenType.RPAREN, self.current_char)
            case ';':
                tok = self.__new_token(TokenType.SEMICOLON, self.current_char)
            case '=':
                # Handle '=='
                if self.__peek_char() == '=':
                    ch = self.current_char
                    self.__read_char()
                    tok = self.__new_token(TokenType.EQ, ch + self.current_char)
                else:
                    tok = self.__new_token(TokenType.ASSIGN, self.current_char)
            case '!':
                # Handle '!='
                if self.__peek_char() == '=':
                    ch = self.current_char
                    self.__read_char()
                    tok = self.__new_token(TokenType.NOT_EQ, ch + self.current_char)
                else:
                    tok = self.__new_token(TokenType.BANG, self.current_char)
            case '<':
                # Handle '<='
                if self.__peek_char() == '=':
                    ch = self.current_char
                    self.__read_char()
                    tok = self.__new_token(TokenType.LT_EQ, ch + self.current_char)
                else:
                    tok = self.__new_token(TokenType.LT, self.current_char)
            case '>':
                # Handle '>='
                if self.__peek_char() == '=':
                    ch = self.current_char
                    self.__read_char()
                    tok = self.__new_token(TokenType.GT_EQ, ch + self.current_char)
                else:
                    tok = self.__new_token(TokenType.GT, self.current_char)
            case '{':
                tok = self.__new_token(TokenType.LBRACE, self.current_char)
            case '}':
                tok = self.__new_token(TokenType.RBRACE, self.current_char)
            case ',':
                tok = self.__new_token(TokenType.COMMA, self.current_char)
            case "[":
                tok = self.__new_token(TokenType.LBRACKET, self.current_char)
            case "]":
                tok = self.__new_token(TokenType.RBRACKET, self.current_char)
            case ":":
                tok = self.__new_token(TokenType.COLON, self.current_char)
            case '"':
                tok = self.__new_token(TokenType.STRING, self.__read_string())
            case None:
                tok = self.__new_token(TokenType.EOF, "")
            case _:
                if self.__is_letter(self.current_char):
                    literal = self.__read_identifier()
                    ttype = lookup_ident(literal)
                    tok = self.__new_token(tt=ttype, char=literal)
                    return tok
                elif self.__is_digit(self.current_char):
                    tok = self.__read_number()
                    return tok
                else:
                    tok = self.__new_token(TokenType.ILLEGAL, self.current_char)

        self.__read_char()
        return tok
    # endregion

    # region Execution Helpers
    def __new_token(self, tt: TokenType, char: str) -> Token:
        return Token(token_type=tt, literal=char)

    def __skip_whitespace(self) -> None:
        while self.current_char in [' ', '\t', '\n', '\r']:
            self.__read_char()

    def __skip_comment(self) -> None:
        while self.current_char is not None and not self.current_char == '\n':
            self.__read_char()

    def __is_letter(self, ch: str) -> bool:
        return 'a' <= ch and ch <= 'z' or 'A' <= ch and ch <= 'Z' or ch == '_'
    
    def __is_digit(self, ch: str) -> bool:
        return '0' <= ch and ch <= '9'
    
    def __read_string(self) -> str:
        position: int = self.position + 1
        while True:
            self.__read_char()
            if self.current_char == '"' or self.current_char is None:
                break
        return self.source[position:self.position]
    
    def __read_number(self) -> Token:
        start_pos: int = self.position
        dot_count: int = 0

        output: str = ""
        while self.__is_digit(self.current_char) or self.current_char == '.':
            if self.current_char == '.':
                dot_count += 1
            
            if dot_count > 1:
                print("Too many dots in number")
                return self.__new_token(TokenType.ILLEGAL, self.source[start_pos:self.position])

            output += self.source[self.position]
            self.__read_char()

            if self.current_char is None:
                break
        
        if dot_count == 0:
            return self.__new_token(TokenType.INT, output)
        else:
            return self.__new_token(TokenType.FLOAT, output)\
            
    def __read_identifier(self) -> str:
        position = self.position
        while self.__is_letter(self.current_char) or self.current_char.isalnum():
            self.__read_char()
        
        return self.source[position:self.position]
    # endregion