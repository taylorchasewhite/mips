# -*- coding: utf-8 -*-
__author__ = "Robert Smayda, Taylor White [taylorchasewhite.com]"

import re
from collections import deque


class Lexer:
    reservedWords = {
        word: word.upper() for word in
        "begin end read write int string bool if else while True False and or not".split()
    }
    operators = {
        "+": "PLUS", "-": "MINUS", "*": "MULT", "/": "DIV", "%": "MOD",
        "==": "EQUALTO", "!=": "NOT_EQUALS", "<": "LESSTHAN", ">": "GREATERTHAN",
        "<=": "LESS_EQUALS", ">=": "GREATER_EQUALS", "&&": "AND", "||": "OR",
        "!": "NOT", "(": "LPAREN", ")": "RPAREN", ";": "SEMICOLON",
        ",": "COMMA", ":=": "ASSIGNOP", "{": "LCURLY", "}": "RCURLY",
    }
    token = re.compile(
        r'(?P<STRINGLITERAL>"(?:\\["\\nt]|[^"\\\r\n])*")'
        r'|(?P<ID>[a-zA-Z_][a-zA-Z_0-9]*)'
        r'|(?P<INTLITERAL>[0-9]+)'
        r'|(?P<OP>:=|==|!=|<=|>=|&&|\|\||[+\-*/%<>!();,{}])'
    )

    def __init__(self, fileList):
        self.lines = iter(fileList)
        self.tokenList = deque()
        self.lineCount = 0

    def getNextWord(self):
        while not self.tokenList:
            line = next(self.lines, None)
            if line is None:
                return "done"
            self.lineCount += 1
            position = 0
            while position < len(line):
                if line[position].isspace():
                    position += 1
                    continue
                match = self.token.match(line, position)
                if match is None:
                    raise ValueError(
                        f"Lexical error on line {self.lineCount}, column {position + 1}: "
                        f"unrecognized token or invalid string near {line[position:position + 20]!r}."
                    )
                kind, value = match.lastgroup, match.group()
                if kind == "ID":
                    kind = self.reservedWords.get(value, "ID")
                elif kind == "OP":
                    kind = self.operators[value]
                elif kind == "STRINGLITERAL":
                    value = value[1:-1]
                self.tokenList.append(kind + "|~ " + value)
                position = match.end()
        return self.tokenList.popleft()

    def getLine(self):
        return self.lineCount
