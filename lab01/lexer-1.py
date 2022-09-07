#
# T-603-THYD Compilers
# Project: Lexer Skeleton for ChocoPy 2022
#
import io
from enum import Enum
from typing import NamedTuple


# The token types the Lexer recognizes.
class Tokentype(Enum):
    EOI = 0  # end of input
    Unknown = 1  # unknown

    # Operators
    OpOr = 2  # or
    OpAnd = 3  # and
    OpNot = 4  # not

    # Punctuation marks
    ParenthesisL = 5  # (
    ParenthesisR = 6  # )

    # Other
    BoolTrueLiteral = 7  # True
    BoolFalseLiteral = 8  # False


class Location(NamedTuple):
    line: int
    col: int


class Token(NamedTuple):
    type: Tokentype
    lexeme: str
    location: Location


class SyntaxErrorException(Exception):
    def __init__(self, message, loc):
        self.message = message
        self.location = loc


class Lexer:
    # Private map of reserved words.
    __reserved_words = {
        "or": Tokentype.OpOr,
        "and": Tokentype.OpAnd,
        "not": Tokentype.OpNot,
        "True": Tokentype.BoolTrueLiteral,
        "False": Tokentype.BoolFalseLiteral
    }

    def __read_next_char(self):
        """
        Private helper routine. Reads the next input character, while keeping
        track of its location within the input file.
        """
        if self.eof:
            self.ch = ''
            return

        if self.ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        self.ch = self.f.read(1)

        if not self.ch:  # eof
            self.ch = ''
            self.eof = True

    def __init__(self, f):
        """
        Constructor for the lexer.
        :param: f handle to the input file (from open('filename')).
        """
        self.f, self.ch, self.line, self.col = f, '', 1, 0
        self.eof = False
        self.__read_next_char()  # Read in the first input character (self.ch).

    def next(self):
        """
        Match the next token in input.
        :return: Token with information about the matched Tokentype.
        """

        # Remove white spaces.
        while not self.eof and self.ch.isspace():
            self.__read_next_char()

        # Record the start location of the lexeme we're matching.
        loc = Location(self.line, self.col)

        # Now, try to match a lexeme.
        if self.ch == '':
            token = Token(Tokentype.EOI, self.ch, loc)
        elif self.ch == '(':
            token = Token(Tokentype.ParenthesisL, self.ch, loc)
            self.__read_next_char()
        elif self.ch == ')':
            token = Token(Tokentype.ParenthesisR, self.ch, loc)
            self.__read_next_char()
        else:
            if self.ch.isalpha():
                chars = []
                while self.ch.isalpha():
                    chars.append(self.ch)
                    self.__read_next_char()
                name = ''.join(chars)
                token = Token(self.__reserved_words.get(name, Tokentype.Unknown), name, loc)
            else:
                token = Token(Tokentype.Unknown, self.ch, loc)
                self.__read_next_char()

        return token
