#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = "3.3"
__author__ = "Robert Smayda, Taylor White [taylorchasewhite.com]"

import re
import sys
import fileinput
from collections import defaultdict
from lexer import Lexer
from codeGen import CodeGenerator
from record import Record

""" LEXER Methods"""
#
# getNextWord() returns [BEGIN, begin] -or- [TOKEN NAME, TOKEN VALUE]
# getLine()     returns lineNumber as int
""" END LEXER"""

""" PARSER CLASS """
bDivide = "\n---------------------\n"
fDivide = "\n---------------------"
class Compiler:
    
    """Parse the line"""
    # initialize
    def __init__(self):
        outFile = ""
        #READ - IN#
        if len(sys.argv)>2:
            fileName = sys.argv[1]
            outFile = sys.argv[2]
            x = open(fileName)
        else:
            x = open("testr.txt")
            outFile = "test.asm"
        #DONE#
        self.fileList = x.readlines()
        self.tokenVal   = []
        self.tokenName  = []
        self.line       = []
        self.lex        = Lexer(self.fileList)
        self.codeGen    = CodeGenerator(outFile)
        self.output     = ""
        self.outputFile = ""
        self.firstVar   = ""
        self.secondVar  = ""
        self.arith      = ""
        self.readString = ""
        self.programCount = 0
        self.endFound = False
        self.completedParse = False

        self.lastRec = Record("bullshit","asdf", "DONT USE")
        self.writeString = []
        
        #self.program()
    ###                             PRODUCTION METHODS                              ###
    ###################################################################################
    ###                                                                             ###
    ###################################################################################
    ###                                                                             ###
        
    """-----------------------------------------------------------------------------"""       
    """                              PROGRAM                                        """
    """-----------------------------------------------------------------------------"""
    def program(self):
        if(self.completedParse):
            return False        
        self.begin()
        self.endFound = False;
        self.statement_list()
        self.end()
        ##xprint(fDivid)
        self.printFinalProg()
        
    """-----------------------------------------------------------------------------"""       
    """                              BEGIN                                          """
    """-----------------------------------------------------------------------------"""
    def begin(self):
        self.codeGen.start()
        if(self.completedParse):
            return False
        ##xprint("Starting to lex");          #TO TEST LEXER!!
        #while(self.breakNextWord()):
        #    #xprint("")
        if(self.breakNextWord()):
            #self.parseOutput("Program " + str(self.programCount) + ":")
            if(self.tokenName[0] != "BEGIN" and not self.completedParse):
                self.parseError("'begin' is required at the start of the program.");
            else:
                return
        else:
            self.parseError("Empty File.");

    """-----------------------------------------------------------------------------"""       
    """                              CONTENT                                        """
    """-----------------------------------------------------------------------------"""
    def content(self, breakNextWord = True): # assuming you don't need to call next token when entering
        if(self.completedParse):
            return False
        if(self.breakNextWord() and not self.completedParse):
            if(not self.completedParse and self.tokenName[-1] != "LCURLY"):
                #xprint("looking for Lcurly "+self.tokenName[-1])
                self.parseError("Missing \'{\' at the end of the conditional statement")

            if (self.statement_list(breakNextWord)):
                print()
              #  self.breakNextWord();
            
            if(not self.completedParse and not (self.tokenName[-1] == "RCURLY" or (self.tokenName[-2] == "RCURLY" and self.tokenName[-1] == "END"))):
                #xprint("looking for Rcurly "+self.tokenName[-1])
                self.parseError("Missing \'}\' at the end of the conditional statement")
            return True;
            

    """-----------------------------------------------------------------------------"""       
    """                              STATEMENT LIST                                 """
    """-----------------------------------------------------------------------------"""
    def statement_list(self, breakNextWord = True):
        if(self.completedParse):
            return False
        if(breakNextWord and not self.completedParse):
             self.breakNextWord();
        if(not self.completedParse and self.tokenName[-1] == "END"):
            return False
        if (not self.completedParse and self.tokenName[-1] == "RCURLY"):
            return True;
        ##xprint("right before statment: "+self.tokenName[-1])
        if (self.statement() and not self.completedParse): # do I need to get another token?
            self.breakNextWord();

        #if (self.tokenName[-2] == "RCURLY"):
        return self.statement_list(False)   
        
        if (not self.completedParse and self.tokenName[-(1)] == "SEMICOLON"):
            self.statement_list()
            return False;

        if (not self.completedParse and self.tokenName[-(1)] == "RCURLY"):
            return True;

        if (not self.completedParse and self.tokenName[-(2)] == "RCURLY" and (self.tokenName[-(1)] == "END")):
            return False;
        
        elif (not self.completedParse):
            #xprint("SL2: "+self.tokenName[-1])
            self.parseError("Missing \';\' in the statement")
                
        return False; #do not need to get another token


    """-----------------------------------------------------------------------------"""       
    """                              STATEMENT                                      """
    """-----------------------------------------------------------------------------"""
    def statement(self):
        if(self.completedParse):
            return False
        return self.checkStatementType()

    """-----------------------------------------------------------------------------"""       
    """                              SEMI-COLON                                     """
    """-----------------------------------------------------------------------------"""
    def semi_col(self, breakNext = True):
        if (not self.completedParse and breakNext):
            self.breakNextWord()
        if (not self.completedParse and self.tokenName[-1] != "SEMICOLON"):
            self.parseError("Missing \';\' in the statement")
        return True;
        

    
    """-----------------------------------------------------------------------------"""       
    """                              CHECK STATEMENT TYPE                           """
    """-----------------------------------------------------------------------------"""
    def checkStatementType(self):
        if(self.completedParse):
            return False        
        if (self.identity(False)):
            return self.semi_col(self.id_statement())       #   ID := <expression>
        elif (self.tokenName[-1] == "INT" or self.tokenName[-1] == "STRING" or  self.tokenName[-1] == "BOOL"):
            return self.semi_col(self.type_dec());             #  <type> <id>
        elif (self.tokenName[-1] == "READ"):
            return self.semi_col(self.read_statement());       #   read(<id list>)
        elif (self.tokenName[-1] == "WRITE"):
            return self.semi_col(self.write_statement());       #   write( <expr list> )
        elif (self.tokenName[-1] == "WHILE"):
            return self.w_condition();          #   while <condition> <content>
        elif (self.tokenName[-1] == "IF"):
            self.if_condition()                 #   if <condition> <content> {else <content>}
            if (self.tokenName[-1] == "END"):
                return False;
            ##xprint("Else current= " + self.tokenName[-1]+ " & before that " + self.tokenName[-2]+self.tokenName[-3]);
            if (not self.completedParse and self.breakNextWord()):
                
                if (not self.completedParse and self.tokenName[-1] != "ELSE"):
                    ##xprint("no Else current= " + self.tokenName[-1]+ " & before that " + self.tokenName[-2]+self.tokenName[-3]);
                    self.codeGen.endIf(self.lex.getLine())# put the else label here
                    #xprint("if: "+self.tokenName[-1])
                    if (self.tokenName[-1] == "END"):
                        return False;
                    return False;
                ##xprint("Else current= " + self.tokenName[-1])
                result = self.content();
                self.codeGen.endIf(self.lex.getLine())
                #xprint("Else is done!!")
                return result;
            return False;
        else:
            #xprint(self.tokenName[-1]+": is not a statement type")
            self.parseError(self.tokenName[-1]+": is not a statement type")
    """-----------------------------------------------------------------------------"""       
    """                              w_condition                                    """
    """-----------------------------------------------------------------------------"""
    def w_condition(self):
        if(self.completedParse):
            return False
        if (not self.completedParse and self.breakNextWord()):
            if (not self.completedParse and self.tokenName[-1] != "LPAREN"):
                self.parseError("Missing LPAREN in the while statement")

        count = self.codeGen.whileLabel(self.lex.getLine()) # generate if Label
        self.expression(True);
        rec = self.lastRec
        if (not self.completedParse and self.tokenName[-1] != "RPAREN"): #breakNextWord called in id_list()
            self.parseError("Missing RPAREN in the while statement")
        self.codeGen.whileStart(rec, count, self.lex.getLine()) # generate if Label
        self.content();
        self.codeGen.whileEnd(count, self.lex.getLine())
        #xprint("While is done!!");
        
        return True; # Need to call the next token
    """-----------------------------------------------------------------------------"""       
    """                              if_condition                                   """
    """-----------------------------------------------------------------------------"""
    def if_condition(self):
        if(self.completedParse):
            return False
        if (not self.completedParse and self.breakNextWord()):
            if (not self.completedParse and self.tokenName[-1] != "LPAREN"):
                self.parseError("Missing LPAREN in the if statement")
        self.expression(True);
        rec = self.lastRec
        if (not self.completedParse and self.tokenName[-1] != "RPAREN"): #breakNextWord called in id_list()
            self.parseError("Missing RPAREN in the if statement")
        count = self.codeGen.ifStart(rec, self.lex.getLine()) # generate if Label
        self.content();
        #xprint("If is done!!");
        self.codeGen.elseStart(count, self.lex.getLine()) # go to the else part(!)
        return False; # Need to call the next token


    """-----------------------------------------------------------------------------"""       
    """                              ID STATEMENT                                   """
    """-----------------------------------------------------------------------------"""
    def id_statement(self):
        toAssign = self.tokenVal[-1]
        if(self.completedParse):
            return False
        if (self.breakNextWord() and not self.completedParse):
            if (self.tokenName[-1] != "ASSIGNOP"):
                self.parseError("Expected ASSIGNOP after ID")
                # did not get an expected assign op. This is a syntax error.
            else:
                if(self.expression(True)):
                    return True
                
                if (self.lastRec == False):
                    result = False
                else:
                    result = self.lastRec.mipsVar
                #xprint("Assigning!!: "+toAssign)
                self.codeGen.assign(toAssign, result, self.lex.getLine())
                return False; # Need to call the next token
        elif (not self.completedParse):
            self.parseError()
            # unexpected EOF error

    """-----------------------------------------------------------------------------"""       
    """                              Type (Declare)                                 """
    """-----------------------------------------------------------------------------"""
    def type_dec(self):
        if(self.completedParse):
            return False
        typ = self.tokenVal[-1]
        if (self.breakNextWord() and not self.completedParse):
            if (not self.identity(True)):
                self.parseError(self.tokenVal[-1]+": is not a valid ID")
            if (self.lastRec == False):
                result = False
            else:
                result = self.lastRec.mipsVar
             #TODO
            #xprint("Declaring!!: "+self.tokenVal[-1])
            self.codeGen.declare(self.tokenVal[-1], typ, self.lex.getLine()) # changed from result to typ
                
            return True; # Need to call the next token
        elif (not self.completedParse):
            self.parseError()
            
            
    """-----------------------------------------------------------------------------"""       
    """                              WRITE STATEMENT                                """
    """-----------------------------------------------------------------------------"""
    def write_statement(self):
        if(self.completedParse):
            return False
        ##xprint("WriteVal1: "+self.tokenVal[-1])
        if (not self.completedParse and self.breakNextWord()):
            if (not self.completedParse and self.tokenName[-1] != "LPAREN"):
                self.parseError("Missing LPAREN in the write statement")
        self.expression_list();
        if (not self.completedParse and self.tokenName[-1] != "RPAREN"): #breakNextWord called in id_list()
            self.parseError("Missing RPAREN in the write statement")
        #xprint("Writing!!: "+', '.join(self.writeString) )
        self.codeGen.write_exprs(self.writeString, self.lex.getLine())
        
        self.writeString = []
        return True; # Need to call the next token

    """-----------------------------------------------------------------------------"""       
    """                              READ STATEMENT                                 """
    """-----------------------------------------------------------------------------"""
    def read_statement(self) :
        if(self.completedParse):
            return False
        if (not self.completedParse and self.breakNextWord()):
            if (not self.completedParse and self.tokenName[-1] != "LPAREN"):
                self.parseError("Missing LPAREN in the read statement")
                
        self.id_list();
        
        if (not self.completedParse and self.tokenName[-1] != "RPAREN"): #breakNextWord called in id_list()
                self.parseError("Missing RPAREN in the read statement")
        #xprint("Reading!!: "+', '.join(self.readString) )  
        self.codeGen.read_ids(self.readString, self.lex.getLine())
        
        self.readString = ""
        return True; # Need to call the next token

    """-----------------------------------------------------------------------------"""       
    """                              EXPRESSION_LIST                                """
    """-----------------------------------------------------------------------------"""
    def expression_list(self):
        if(self.completedParse):
            return False
        ##xprint("exp_List0: "+self.tokenVal[-1])
        if (not self.completedParse and self.expression(True)):
            self.breakNextWord()
        ##xprint("exp_List1: "+self.tokenVal[-1])
        writeState = ""
        if (self.lastRec == False):
            writeState = False;
        else:
            writeState = self.lastRec.mipsVar
        self.writeString.append(str(writeState))
        if (not self.completedParse and self.tokenName[-1] == "COMMA"):
            self.expression_list();
       # #xprint("exp_List: "+self.tokenVal[-1])
        return False # comma was not found. Next token waiting.


    """-----------------------------------------------------------------------------"""       
    """                              EXPRESSION                                     """
    """-----------------------------------------------------------------------------"""
    def expression(self, first):
        ##xprint("EXP1: "+self.tokenVal[-1])
        ##xprint("expression!")
        firstVar = ""                                                               # declare firstVar
        secondVar = ""                                                              # declare secondVar
        bool_op = ""                                                                # declare bool op ??
        if(self.completedParse):                                                    # if we're done
            return False                                                            # fail
        
        if (first and self.exp2(True)): # we got a primary                       # no idea
            i = 0 #WTF?                                                             # no idea
        ##xprint("after bool\t " + str(self.lastRec.srcVar) + " " + str(self.lastRec.mipsVar) + " " + str(self.lastRec.rType))
        if (self.lastRec == False):                                                 # no idea
            firstVar = False;                                                       # no idea
        else:
            firstVar = self.lastRec.mipsVar
      #  self.breakNextWord()    # check the next word if we got an operation
        
        if(not self.completedParse and (self.tokenName[-1] == "OR")): # if the next word is a AND/OR
            bool_op = self.tokenVal[-1]
          #  #xprint("EXP2: "+self.tokenVal[-1])
            if(not self.completedParse and self.exp2(True)):     # if we got a ID | intLiteral
                # changed this back...
                # what does going into this if statement versus not going into it mean?
                self.parseOutput(self.tokenVal[-1])
                if (self.lastRec == False):
                    secondVar = False;
                else:
                    secondVar = self.lastRec.mipsVar

                #xprint("BOOL_OP\t" + firstVar + "\t" + str(bool_op) +self.tokenVal[-1])
                #TODO
                self.lastRec = self.codeGen.bool_op(bool_op, firstVar, secondVar, self.lex.getLine())
              #  #xprint("EXP3: "+self.tokenVal[-1])
                if (not self.tokenName[-1] == "RPAREN" and not self.tokenName[-1] == "SEMICOLON"):
                    u=0 #WTF?
                    #self.breakNextWord()
                self.expression(False); # to enable extra OR's
                return False
                
        #elif (not self.completedParse):
        ##xprint("before return\t " + str(self.lastRec.srcVar) + " " + str(self.lastRec.mipsVar) + " " + str(self.lastRec.rType))
        return False
    """-----------------------------------------------------------------------------"""       
    """                              EXP2                                           """
    """-----------------------------------------------------------------------------"""
    def exp2(self, first):
        firstVar = ""
        secondVar = ""
        # = ""
        if(self.completedParse):
            return False
        if (first and self.boolean(True)): # we got a primary
            i = 0
        if (self.lastRec == False):
            firstVar = False;
        else:
            firstVar = self.lastRec.mipsVar
        ##xprint("bool1: "+self.tokenVal[-1])
        #self.breakNextWord()    # check the next word if we got a primary
        ##xprint("bool2: "+self.tokenVal[-1])
        if(not self.completedParse and (self.tokenName[-1] == "AND")): # if the next word is a num_op
            bool_op = self.tokenVal[-1]
            
            if(not self.completedParse and self.boolean(True)):  
                
                self.parseOutput(self.tokenVal[-1])
                
                if (self.lastRec == False):
                    secondVar = False;
                else:
                    secondVar = self.lastRec.mipsVar

                #xprint("num_op!!: "+firstVar+ str(num_op) +self.tokenVal[-1])# str(secondVar))
                self.lastRec = self.codeGen.bool_op(bool_op, firstVar, secondVar, self.lex.getLine())
                ##xprint("!\t " + str(self.lastRec.srcVar) + " " + str(self.lastRec.mipsVar) + " " + str(self.lastRec.rType))
                self.exp2(False); # to enable extra AND's
                return True
                
        #elif (not self.completedParse):
        ##xprint("TERM3: "+self.tokenVal[-1])
        return True
    
    
    """-----------------------------------------------------------------------------"""       
    """                              BOOLEAN                                        """
    """-----------------------------------------------------------------------------"""
    def boolean(self, first):
        firstVar = ""
        secondVar = ""
        # = ""
        if(self.completedParse):
            return False
        if (first and self.clause(True)): # we got a primary
            i = 0
        if (self.lastRec == False):
            firstVar = False;
        else:
            firstVar = self.lastRec.mipsVar
        ##xprint("bool1: "+self.tokenVal[-1])
        #self.breakNextWord()    # check the next word if we got a primary
        ##xprint("bool2: "+self.tokenVal[-1])
        if(not self.completedParse and self.num_op()): # if the next word is a num_op
            num_op = self.tokenVal[-1]
            
            if(not self.completedParse and self.clause(True)):  
                
                self.parseOutput(self.tokenVal[-1])
                
                if (self.lastRec == False):
                    secondVar = False;
                else:
                    secondVar = self.lastRec.mipsVar

                #xprint("num_op!!: "+firstVar+ str(num_op) +self.tokenVal[-1])# str(secondVar))
                self.lastRec = self.codeGen.num_op(num_op, firstVar, secondVar, self.lex.getLine())
                ##xprint("!\t " + str(self.lastRec.srcVar) + " " + str(self.lastRec.mipsVar) + " " + str(self.lastRec.rType))
                self.boolean(False); # to enable extra num_ops's
                return True
                
        #elif (not self.completedParse):
        ##xprint("TERM3: "+self.tokenVal[-1])
        return True
    """-----------------------------------------------------------------------------"""       
    """                              NUM_OP                                     """
    """-----------------------------------------------------------------------------"""
    def num_op(self):
        if (self.tokenName[-1] == "EQUALTO" or self.tokenName[-1] == "LESSTHAN" or self.tokenName[-1] == "GREATERTHAN" or
            self.tokenName[-1] == "LESS_EQUALS" or self.tokenName[-1] == "GREATER_EQUALS" or self.tokenName[-1] == "NOT_EQUALS"):
            return True;
        else:
            return False;


    """-----------------------------------------------------------------------------"""       
    """                              clause                                         """
    """-----------------------------------------------------------------------------"""
    def clause(self, first):
        ##xprint("EXP1: "+self.tokenVal[-1])
        firstVar = ""
        secondVar = ""
        arith = ""
        if(self.completedParse):
            return False
        
        if (first and self.term(True)): # we got a primary
            i = 0
        if (self.lastRec == False):
            firstVar = False;
        else:
            firstVar = self.lastRec.mipsVar
      #  self.breakNextWord()    # check the next word if we got an operation
        
        if(not self.completedParse and self.plus_op()): # if the next word is a +/-
            arith = self.tokenVal[-1]
          #  #xprint("EXP2: "+self.tokenVal[-1])
            if(not self.completedParse and self.term(True)):     # if we got a ID | intLiteral
                # changed this back...
                # what does going into this if statement versus not going into it mean?
                self.parseOutput(self.tokenVal[-1])
                if (self.lastRec == False):
                    secondVar = False;
                else:
                    secondVar = self.lastRec.mipsVar

                #xprint("Adding!!: "+firstVar+ str(arith) +self.tokenVal[-1])# str(secondVar))
                self.lastRec = self.codeGen.add_op(arith, firstVar, secondVar, self.lex.getLine())
              #  #xprint("EXP3: "+self.tokenVal[-1])
                if (not self.tokenName[-1] == "RPAREN" and not self.tokenName[-1] == "SEMICOLON"):
                    u=0
                    #self.breakNextWord()
                self.clause(False); # to enable extra +'s
                return True #changed
                
        #elif (not self.completedParse):
       # #xprint("EXP3: "+self.tokenVal[-1])
        return True #changed
        
    """-----------------------------------------------------------------------------"""       
    """                              PLUS_OP                                     """
    """-----------------------------------------------------------------------------"""
    def plus_op(self):
        if (self.tokenName[-1] == "PLUS" or self.tokenName[-1] == "MINUS"):
            return True;
        else:
            return False;

    """-----------------------------------------------------------------------------"""       
    """                              TERM                                     """
    """-----------------------------------------------------------------------------"""
    def term(self, first):
        firstVar = ""
        secondVar = ""
        arith = ""
        if(self.completedParse):
            return False
        if (first and self.factor()): # we got a primary
            i = 0
        if (self.lastRec == False):
            firstVar = False;
        else:
            firstVar = self.lastRec.mipsVar
        ##xprint("TERM1: "+self.tokenVal[-1])
        self.breakNextWord()    # check the next word if we got a primary
        ##xprint("TERM2: "+self.tokenVal[-1])
        if(not self.completedParse and self.mult_op()): # if the next word is a *///%
            arith = self.tokenVal[-1]
            
            if(not self.completedParse and self.factor()):     # if we got a ID | intLiteral
                
                self.parseOutput(self.tokenVal[-1])
                
                if (self.lastRec == False):
                    secondVar = False;
                else:
                    secondVar = self.lastRec.mipsVar

                #xprint("Multiplying!!: "+firstVar+ str(arith) +self.tokenVal[-1])# str(secondVar))
                self.lastRec = self.codeGen.mult_op(arith, firstVar, secondVar, self.lex.getLine())

                self.term(False); # to enable extra *'s
            return True
                
        #elif (not self.completedParse):
        ##xprint("TERM3: "+self.tokenVal[-1])
        return True

    """-----------------------------------------------------------------------------"""       
    """                              MULT_OP                                     """
    """-----------------------------------------------------------------------------"""
    def mult_op(self):
        if (self.tokenName[-1] == "MULT" or self.tokenName[-1] == "DIV" or self.tokenName[-1] == "MOD"):
            return True;
        else:
            return False;

    """-----------------------------------------------------------------------------"""       
    """                              FACTOR                                     """
    """-----------------------------------------------------------------------------"""
    def factor(self):
        ##xprint("IN FACT0: "+self.tokenName[-1])
        if(self.completedParse):
            return False
        if(self.breakNextWord() and not self.completedParse):
           # #xprint("IN FACT1: "+self.tokenName[-1])
            if (self.neg_op()):
                self.breakNextWord()
                if (self.primary()):
                    ##xprint("IN FACT2: "+self.tokenName[-1])
                    self.parseOutput(self.tokenVal[-1])
                    
                    if (self.lastRec == False):
                        negVar = False;
                    else:
                        negVar = self.lastRec.mipsVar
                    #xprint("Negating!!: "+self.tokenVal[-1])
                    self.lastRec = self.codeGen.negate_term(negVar, self.lex.getLine())
                    return True;
            else:
                self.primary()
                ##xprint("IN FACT3: "+self.tokenName[-1])
                return True
        return False;
                

    """-----------------------------------------------------------------------------"""       
    """                              NEG_OP                                     """
    """-----------------------------------------------------------------------------"""
    def neg_op(self):
        if (self.tokenName[-1] == "MINUS" or self.tokenName[-1] == "NOT"):
            return True;
        else:
            return False;
        
    """-----------------------------------------------------------------------------"""       
    """                              ID_LIST                                        """
    """-----------------------------------------------------------------------------"""
    def id_list(self):
        if(self.completedParse):
            return False
        if (not self.completedParse and self.breakNextWord()):
            if (not self.completedParse and not self.identity(True)):
                self.parseError("Only ID's followed by a \',\' can be within read statments") ## return FALSE?

        x = ""
        if (self.lastRec == False):
            x = False;
        else:
            x = self.lastRec.mipsVar
        self.readString= self.readString+ str(x)
        
        if (not self.completedParse and self.breakNextWord()):
            if (not self.completedParse and self.tokenName[-1] == "COMMA"):
                self.readString = self.readString+","
                self.id_list();
        return False # comma was not found. Next token waiting.


    """-----------------------------------------------------------------------------"""       
    """                              PRIMARY                                        """
    """-----------------------------------------------------------------------------"""
    def primary(self):
        if(self.completedParse):
            return False
        elif( not self.completedParse and self.tokenName[-1] == "LPAREN"):             # we got a left paren, have to get an expression inbetween
            if (not self.completedParse and self.expression(True)):                      # see if we got an expression between
                self.breakNextWord()                                                # if so, check next word
            if(not self.completedParse and self.tokenName[-1] != "RPAREN"):
                self.parseError("Missing RPAREN")
            else:                                                                   # returning, primary True
                return True
        elif(not self.completedParse and self.tokenName[-1] =="ID"):
            return self.identity(True) # changed true
        elif(not self.completedParse and self.tokenName[-1] =="INTLITERAL"):

            #xprint("Processing int literal!!: " + self.tokenVal[-1])
            self.lastRec = self.codeGen.process_literal(self.tokenVal[-1], self.lex.getLine())
            return True                                                             # is a primary if we got an ID or IntLiteral
        elif(not self.completedParse and self.tokenName[-1] =="STRINGLITERAL"):

            #xprint("Processing String literal!!: " + self.tokenVal[-1])
            self.lastRec = self.codeGen.process_string_literal(self.tokenVal[-1], self.lex.getLine())
            return True;
        elif(not self.completedParse and (self.tokenName[-1] =="TRUE" or self.tokenName[-1] =="FALSE")):

            #xprint("Processing Bool literal!!: " + self.tokenVal[-1])
            self.lastRec = self.codeGen.process_bool_literal(self.tokenVal[-1], self.lex.getLine())
            return True;
        elif(not self.completedParse):
            #xprint(self.tokenName[-1]+ " is not a Primary")
            self.parseError(self.tokenName[-1]+ " is not a Primary")
        elif (not self.completedParse):
            self.parseError("Unexpected EOF")                                           # end, no primary

    """-----------------------------------------------------------------------------"""       
    """                              IDENTITY                                         """
    """-----------------------------------------------------------------------------"""
    def identity(self, readCall):               
        if(self.completedParse):
            return False
        if(not self.completedParse and self.tokenName[-1] =="ID" ):
            #xprint("Processing ID!!: " + self.tokenVal[-1])
            self.lastRec = self.codeGen.process_id(self.tokenVal[-1], readCall) # give type
            return True
        elif (not self.completedParse):
            return False
            #self.parseError(self.tokenName[-1]+" is not an identity. ADDED ERROR") # invalid syntax <primary>followed not by <arith op>


    """-----------------------------------------------------------------------------"""       
    """                              END                                            """
    """-----------------------------------------------------------------------------"""
    def end(self):
        if(self.completedParse):
            return False
        if(not self.completedParse and self.tokenName[-1] == "END"):
            if(not self.completedParse and self.breakNextWord(True)):
                if(not self.completedParse and self.tokenName[-1] == "done" or self.tokenName[-1] == "new_pro"):
                    passMsg = ("\nCongratulations, the program "+str(self.programCount)+" has passed parsing. You're the home-diggity")
                    self.parseOutput(passMsg)
                    #xprint(passMsg)
                    self.parseOutput(bDivide)
                    self.newProg()
                elif (not self.completedParse):
                    self.parseError("Invalid input after 'end'")
                    return  
        elif (not self.completedParse):
            #xprint("END ERROR: "+self.tokenName[-1]+self.tokenName[-2]+self.tokenName[-3]+self.tokenName[-4])
            self.parseError("expecting an \'end\'", True)


    ###                              END PRODUCTION METHODS                         ###
    ###################################################################################
    ###                                                                             ###
    ###################################################################################
    ###                              HELPER METHODS                                 ###

    """-----------------------------------------------------------------------------"""       
    """                              PARSE ERROR                                    """
    """-----------------------------------------------------------------------------"""

    def parseError(self, errorMsg = "Need to put a E Message", endError = False):
        if(self.completedParse):
            return False
        error = "\nParse error on line " + str(self.lex.getLine())+": "+errorMsg
        print(error) # if we hit the end here, is it in error?
        self.parseOutput(error)
        ##xprint(bDivide)
        self.parseOutput(bDivide)
        x = self.tokenName[-1]
        if (endError ==False and not self.completedParse):
            while x != "new_pro" and not self.completedParse:
                if(x == "done" and not self.completedParse):
                    sys.exit(0);
                x = self.lex.getNextWord()
        if(x == "done" and not self.completedParse):
            sys.exit(0)
        self.newProg()


    """-----------------------------------------------------------------------------"""       
    """                              PRINT PROGRAM                                  """
    """-----------------------------------------------------------------------------"""
    def printFinalProg(self) :
        for x in range(0, len(self.tokenVal)):
            #xprint(self.tokenName[x] + ", " + self.tokenVal[x])
            self.parseOutput(self.tokenName[x] + ", " + self.tokenVal[x])


    """-----------------------------------------------------------------------------"""       
    """                              PRINT WORD                                     """
    """-----------------------------------------------------------------------------"""
    def printWord(self, x) :
        print(x[0] + ", " + x[1])


    """-----------------------------------------------------------------------------"""       
    """                              TEST METHOD                                    """
    """-----------------------------------------------------------------------------"""
    def testMethod(self):
        print("")

    """-----------------------------------------------------------------------------"""       
    """                              NEW PROGRAM                                    """
    """-----------------------------------------------------------------------------"""
    def newProg(self):
        ##xprint("FINAL PROG")
        #self.printFinalProg()
        if(self.completedParse):
            return False
        self.programCount = self.programCount+1
        self.tokenVal   = []
        self.tokenName  = []
        self.line       = []
        self.lastRec = Record("bullshit","asdf", "DONT USE")
        self.writeString = []
        self.program()
        
    """-----------------------------------------------------------------------------"""       
    """                              BREAK NEXT WORD                                """
    """-----------------------------------------------------------------------------"""
    def breakNextWord(self, cont = False):
        if(self.completedParse):
            return False
        x = self.lex.getNextWord()
        if(x == "new_pro" and not cont and len(self.tokenName) ==0 and not self.completedParse):
            ##xprint("Start of parser\n---------------\n")
            self.parseOutput("Start of parser\n---------------\n")
            self.newProg()
            self.program()
        if(x == "new_pro" and not cont and len(self.tokenName) !=0 and not self.completedParse):
            if(self.tokenName[-1] != "END"):
                return False 
        elif (x=="done" and len(self.tokenName)==0 and not self.completedParse): # we are at the end of the file and exit gracefully.
            self.completedParse = True;
            self.codeGen.finish()
            
            return False
            #sys.exit(0)
        elif(x =="done" and (len(self.tokenName) != 0) and not cont and not self.completedParse):
            if(self.tokenName[-1] != "END" and not self.completedParse):
                return False
                self.parseError("Expected end missing.")
            self.completedParse=True;
            #sys.exit(0) # end gracefully(?)
            return False
        elif(not self.completedParse):
            x = x.split("|~ ")
            ##xself.printWord(x)
            if len(x)>1:
                self.tokenVal.append(x[1])
            self.tokenName.append(x[0])
            return True

    """-----------------------------------------------------------------------------"""       
    """                              Add to Output Parse                             """
    """-----------------------------------------------------------------------------"""
    def parseOutput(self, out):
        self.output = self.output + out

    def getOutput(self):
        return self.output
        
    
    ###                              END HELPER METHODS                             ###
    ###################################################################################
    ###                                                                             ###
    ###################################################################################
    ###                              SEMANTIC & SYMBOL TABLE                        ###



program = Compiler()
program.program()
##xprint(program.getOutput())

""" PROGRAM """

