# -*- coding: utf-8 -*-
__version__ = "3.3"
__author__ = "Robert Smayda, Taylor White [taylorchasewhite.com]"
   

import re
import sys
import fileinput
from collections import defaultdict

class Lexer:
    """CONSTANTS"""
    reservedWords = {"begin":"BEGIN",
                    "end":"END",
                    "read":"READ",
                    "write":"WRITE",
                    "int":"INT",
                    "string":"STRING",
		    "bool":"BOOL",
		    "if":"IF",
		    "else":"ELSE",
		    "while":"WHILE",			
		    "True":"TRUE",			
		    "False":"FALSE",			
		    "and":"AND",
		    "or":"OR",
		    "not":"NOT"}

    identifier = {"ident":"ID"}

    stringLit = {"string":"STRINGLITERAL"}
    
    literals = {"num":"INTLITERAL"}

    arithmeticOps = {"+":"PLUS",
                    "-":"MINUS",
                    "*":"MULT",
                    "/":"DIV",
                    "%":"MOD",
                    "==":"EQUALTO",
                    "<":"LESSTHAN",
                    ">":"GREATERTHAN",
                    "<=":"LESS_EQUALS",
                    ">=":"GREATER_EQUALS",
                    "&&":"AND",
                    "||":"OR",
                     "!=":"NOT_EQUALS",
                    "!":"NOT"}

    symbols = {"(":"LPAREN",
            ")":"RPAREN",
            ";":"SEMICOLON",
            ",":"COMMA",
            ":=":"ASSIGNOP",
            "{":"LCURLY",
            "}":"RCURLY"}
    

    tokenClass = [stringLit, reservedWords, identifier, literals, arithmeticOps, symbols]

    """REGEXES"""
    reservedRegex = "^(begin|end|read|write|int|string|bool|if|else|while|True|False|and|or|not)(.?)"      # does token start and end with these
    identifierRegex = "^([a-zA-Z]\w*)"
    stringLitRegex = "\"(.*?)\""   #"\"([^\"])*\""
    intLiteralRegex = "^(\d+)"
    opsRegex = "^(\+|\-|\*|\/|\%|(==)|(<=)|(>=)|<|>|(&&)|(!=)|(\|\|)|!)"
    symbolsRegex = "^(\(|\)|;|,|(:=)|{|})"

    regexList = [stringLitRegex, reservedRegex, identifierRegex, intLiteralRegex, opsRegex, symbolsRegex]
    """END REGEXES"""

    
    """END CONSTANTS"""
    
    
    def __init__(self, fileList):
        self.tokenList = []
        self.fileList = []
        self.lineCount = 0
        self.fileList = fileList


    def getNextWord(self):
        if self.tokenList:
            return self.tokenList.pop(0)
        if not self.fileList:
            return "done"

        line = self.fileList.pop(0)
        self.lineCount= self.lineCount+1
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                      #MAIN CODE#
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        error=False                                     # No error for now
        quote = "";
        if (line.find('\"')!=-1):                   #cheat to get string regex working
            quPos = line.index('\"')
            quote = line[quPos:]
            #line = line[:quPos]
            line = line[:quPos];#+" "+line[quPos:]
            
        words = line.split();                      # split on ' '
        if (not quote == ""):
            quote = quote.strip();
            #qwords = quote.split();  
            #words = words+qwords
            words.append(quote)
        if not words:
            return self.getNextWord()
        #if words[0].startswith("##########"):
         #   return "new_pro"
        for x in words:
            restart = True
            while restart and not(error):
                x =x.strip();
                i =0;
                #print ("LEX: "+x)
                restart = False
                for regex in Lexer.regexList:
                    m = re.search(regex,x)          #check for regex words
                    if m is not None:
                        word = m.group()
                        #print("word: "+word);
                        if (not x.startswith(word)):
                            i+=1;
                            continue;
                        errorWord = word
                        #print(m.group(1));
                        if i==1 and m.group(2) is not "":
                            t = re.search("(\w)", m.group(2))   
                            if t is not None:       #should be an 'id' restart regex loop
                                i+=1;
                                continue;
                            else:
                                word = word[:-1]    #it is ok remake this a reserve word
                                errorWord = word
                        
                        x= x[x.find(word)+len(word):] # shorten word to look for more tokens
                        TValue = word
                        errorWord = TValue
                        if i == 0:
                            word = "string"
                            TValue = m.group(1) #gets rid of the "s
                        elif i == 2:
                            word = "ident"
                        elif i == 3:
                            word = "num"
                            
                        self.tokenList.append(Lexer.tokenClass[i].get(word) + "|~ " + TValue) #save here
                        #print ("LEXER: "+Lexer.tokenClass[i].get(word) + ", " + TValue);
                        
                        if len(x)>0:            #more left in the word so restart your regex's
                            restart =True
                            break;
                        else:
                            break;
                    i+=1
                    if (i>5): # tried all 6 regexes none match ERROR
                        error = True
                        #print("Errorr" + x)
                        break;
                            
                        
            if error:
                print("\nLexical error on line " + str(self.lineCount)+": Unidentified '" + x +"' please fix this line of code.");
                sys.exit("\nLEXICAL ERROR on line " + str(self.lineCount)+": Unidentified '" + x +"' please fix this line of code.");
            
        return self.tokenList.pop(0)
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                    #END MAIN CODE#
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""  
    def getLine(self):
        return self.lineCount;
