# -*- coding: utf-8 -*-
__version__ = "3.3"
__author__ = "Robert Smayda, Taylor White [taylorchasewhite.com]"

import re
import sys
import fileinput
from collections import defaultdict

###                             NOTES
### By using the system call (syscall) instruction, MARS provides a set of 
### OS-like services. A program requests a specific service by loading the 
### appropriate code into register $v0 with any arguments into $a0-$a3 or 
### $f12 for floating-point values. Return values from system calls are placed
### into register $v0 or $f0. 
###  Example
###  -------
###  li   $v0, 4           # specify Print String service
###  
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###
###

exitCode = "li" + "\t" + "$v0," + "\t" + "10" + "\n" + "syscall"  + "\t\t\t\t\t\t# exit" + "\n"
readInt = "\n" + "li" + "\t" + "$v0," + "\t" + "5" + "\n" + "syscall"  + "\t\t\t\t\t# read in"
readString = "\n" + "li" + "\t" + "$v0," + "\t" + "8" + "\n" + "syscall "  + "\t\t\t\t\t# read in"
writeInt= "li" + "\t" + "$v0," + "\t" + "1" + "\n" + "syscall"  + "\t\t\t\t\t\t# print out"+ "\n"
writeString = "li" + "\t" + "$v0," + "\t" + "4" + "\n" + "syscall"  + "\t\t\t\t\t\t# print out"+ "\n"
hiLoComment = "\t\t\t\t# move from hi/lo"

#Comments
rec0Comment = "\t\t\t# load into register record0"
rec1Comment = "\t\t\t# load into register record1"
swComment = "\t\t\t# store into newVar"
toAssignComment = "\t\t\t# load to be assigned"
getAssignedComment = "\t\t\t\t# load var getting assignment"
loadA0Comment = "\t\t\t\t# load into $a0"
loadA0Comment1 = "\t\t\t# load into $a0"
performOpComment = "\t\t\t\t# perform the operation"
multVarComment = "\t\t\t# mult var dec"
storeValComment = "\t\t\t\t# store the value"
import sys
import fileinput
import re
from record import Record

class CodeGenerator:
    
    def __init__(self, outFile):
        #READ - IN#
        self.outFile = outFile
        self.fileContents = ""
        self.fileData = ""
        self.fileCode = ""
        self.tempExpCount = 0
        self.stringLitCount = 0
        self.boolCount = 0;
        self.whileStartCount = 0;
        self.whileEndCount = 0;
        self.ifCount = 0;
        self.elseCount = 0;
        self.afterIfCount = 0;
        self.symbolTable = []
        self.begin = False
        return

    """-----------------------------------------------------------------------------"""       
    """                              TEST METHOD                                    """
    """-----------------------------------------------------------------------------"""
    #def testMethod(self):
        #xprint("")

    """-----------------------------------------------------------------------------"""       
    """                              START                                          """
    """-----------------------------------------------------------------------------"""
    def start(self):
        ### constants
        if(not self.begin):
            self.addData(".data")
            self.addData("prompt:\t" + ".asciiz" + "\t" + "\"Please provide an integer value: \"")
            self.addData("newLine:\t" + ".asciiz" + "\t" + "\"\\n\"")
            self.addData("defZero:\t" + ".word" + "\t" + "0")
            #self.addData("mipsTrue:\t" + ".word" + "\t" + "1")
#            self.addData("mipsFalse:\t" + ".word" + "\t" + "0")            
            self.addData("mipsSTrue:\t" + ".asciiz" + "\t" + "\"True\"")
            self.addData("mipsSFalse:\t" + ".asciiz" + "\t" + "\"False\"")
            self.addData("mipsTrue:\t" + ".word" + "\t" + "1")
            self.addData("mipsFalse:\t" + ".word" + "\t" + "0")
            self.addToSymbolTable(None,	"mipsTrue", "boolID")
            self.addToSymbolTable(None,	"mipsFalse", "boolID")
            self.addToSymbolTable(None, "prompt", "ID")
            self.addToSymbolTable(None, "newLine", "ID")
            self.addToSymbolTable(None, "defZero", "intID")
            #self.addToSymbolTable("True", "mipsTrue", "BOOLLITERAL")
            #self.addToSymbolTable("False", "mipsFalse", "BOOLLITERAL")
            self.addToSymbolTable("False", "mipsSFalse", "STRINGLITERAL")
            self.addToSymbolTable("True", "mipsSTrue", "STRINGLITERAL")

            ### begin writing the actual code
            self.addCode(".text")
        self.begin = True
    """-----------------------------------------------------------------------------"""       
    """                              FINISH                                         """
    """-----------------------------------------------------------------------------"""        
    def finish(self):
        self.addCode(exitCode)
        self.addCode("writeTrue:")
        self.addCode("move $s0, $ra")
        self.addCode("la $t2, mipsSTrue")
        self.addCode("\n" + "la" + "\t" + "$a0," + "\t" + "mipsSTrue" + loadA0Comment)  # write the list item and not a variable in the symbol table
        self.addCode("beq $t0, 0, writeFalse")
        self.addCode("jr $s0")
        
        self.addCode("writeFalse:")
        self.addCode("la $t2, mipsSFalse")
        self.addCode("\n" + "la" + "\t" + "$a0," + "\t" + "mipsSFalse" + loadA0Comment)  # write the list item and not a variable in the symbol table
        self.addCode("jr $s0")
        
        self.fileContents = self.fileData + "\n" + self.fileCode
        self.writeFile()
        
    """-----------------------------------------------------------------------------"""       
    """                              ASSIGN                                         """
    """-----------------------------------------------------------------------------"""
    def assign(self, left, right, lineNum):
        #xprint("\t\tAssign:\t" + str(left) + ", " + str(right))

        #xself.printSymbolTable()
        left = self.process_id(left, True)                              #  
        #xself.printSymbolTable()
        right = self.getRecUsingMips(right)
        if(not hasattr(left,'rType')):
            self.errMessage(str(lineNum) + ": Variable not recognized.") 
        if(hasattr(left,'rType') and left.rType != "boolID"):
            if (left.rType[:3].lower() != right.rType[:3].lower()):
                self.errMessage("Error at line " + str(lineNum) + ", type reassignment not allowed.") 
                # if it is a string then leave it alone.
        if (right == False):
            self.errMessage("ERROR!! RIGHT side of the ASSIGN is not initialized. Error on line: "+str(lineNum))

        
        if (left.rType == "intID"):                                # if an int
            self.addCode("lw" + "\t" + "$t0" + ",\t" + right.mipsVar + toAssignComment)            
            self.addCode("sw" + "\t" + "$t0" + ",\t" + left.mipsVar+ getAssignedComment)
        elif (left.rType == "boolID"):                             # if a bool
            if(right.rType=="STRINGLITERAL"):
                if(right.mipsVar == "mipsSFalse"):
                    self.addCode("lw" + "\t" + "$t0" + ",\t" + "mipsFalse" + toAssignComment)            
                elif(right.mipsVar == "mipsSTrue"):
                    self.addCode("lw" + "\t" + "$t0" + ",\t" + "mipsTrue" + toAssignComment)
                else:
                    self.errMessage(str(lineNum) + ": Bad boolean assignment.")
            else:
                self.addCode("lw" + "\t" + "$t0" + ",\t" + right.mipsVar + toAssignComment)            
            self.addCode("sw" + "\t" + "$t0" + ",\t" + left.mipsVar+ getAssignedComment)        
        elif(left.rType == "stringID"):
            if(right.mipsVar.startswith("mips")):
                self.addCode("la" + "\t" + "$t0" + ",\t" + right.mipsVar + toAssignComment)
            else:
                self.addCode("lw" + "\t" + "$t0" + ",\t" + right.mipsVar + toAssignComment)            
            self.addCode("sw" + "\t" + "$t0" + ",\t" + left.mipsVar+ getAssignedComment)        
        #elif (result.rType == "INTLITERAL"):
            #TODO # Error causing because mips$ is not 'li' its 'lw'
            #self.addCode("lw" + "\t" + left.mipsVar + ",\t" + right.mipsVar)

    """-----------------------------------------------------------------------------"""
    """                              READ IDS                                       """
    """-----------------------------------------------------------------------------"""
    def read_ids(self,toRead, lineNum):
        print ("\t\ttoRead: " + str(toRead))
                                # we need to ask exactly how this works. If the variable x is not
                                # declared, we add it to symbol table?
                                # what happens if it is declared, do we call assign on it?
                                # right now it just takes the vars and assigns them the user input
        variables = toRead.split(',')
        #xprint(toRead)
        for var in variables:
            rec = self.process_id(var, True) # NEW declare variable
            rec = self.getRecUsingSrc(var)
            if (rec == False):
                self.errMessage(str(lineNum)+": '" + str(var)+"' is not initialized before your READ statement.")
            #self.addCode("\n" + "la" + "\t" + "$a0," + "\t" + "newLine" + "\t\t\t# new line" )
            #self.addCode(writeString)
            #self.addCode("\n" + "la" + "\t" + "$a0," + "\t" + "prompt" + "\t\t\t# prompt")
            #self.addCode(writeString)
            self.addCode(readInt)           # do the read int op.
            self.addCode("sw\t$v0,\t" + var)

    """-----------------------------------------------------------------------------"""       
    """                              WRITE IDS                                       """
    """-----------------------------------------------------------------------------"""     
    def write_exprs(self, toWrite, lineNum):
        #xprint("\t\ttoWRITE: " + str(toWrite))
        self.addCode("\n" + "la" + "\t" + "$a0," + "\t\t" + "newLine")    # go to a new line (aka println)
        self.addCode(writeString)                                       # println
        for w in toWrite:                                                   # toWrite is a list
            rec = self.getRecUsingMips(w)                                   # get the record associated with w
            #xprint("\t\t\tWrite Type: " + rec.mipsVar + " " + rec.rType)
            if rec!= False and rec.rType[:3].lower()== "int":                    # if its a variable--> change just for intIDs and intlits
                #xprint("\t\tID write")
                self.addCode("\n" + "lw" + "\t" + "$a0," + "\t" + rec.mipsVar+ loadA0Comment)        # NOTE: We had 'w' but I changed it to 'rec.mipsVar'
                self.addCode(writeInt)
            elif rec!= False and rec.rType == "INTLITERAL":                 # if its an intLit do something else
                #xprint("\t\tINTLIT write")
                self.addCode("\n" + "lw" + "\t" + "$a0," + "\t" + rec.mipsVar+ loadA0Comment)        #
                self.addCode(writeInt)
            elif (rec != False and rec.rType=="STRINGLITERAL"):
                #xprint("\t\tSTRINGLIT write")
                self.addCode("\n" + "la" + "\t" + "$a0," + "\t" + w+ loadA0Comment)   # write the list item and not a variable in the symbol table
                self.addCode(writeString)
            elif (rec != False and rec.rType=="stringID"):
                #xprint("\t\tSTRINGLIT write")
                self.addCode("\n" + "lw" + "\t" + "$a0," + "\t" + w + loadA0Comment)  # write the list item and not a variable in the symbol table
                self.addCode(writeString)
            elif (rec != False and rec.rType=="boolID"):
                #xprint("\t\tBOOL write")
                self.addCode("lw" + "\t" + "$t0," + "\t" + w)
                self.addCode("jal writeTrue")
                #self.addCode("\n" + "lw" + "\t" + "$a0," + "\t" + "($s2)" + loadA0Comment)  # write the list item and not a variable in the symbol table
                self.addCode(writeString)
            elif rec == False:                                                              # else if its not a STRING LIT and not in the symbol Table
                self.errMessage(str(lineNum) +": "+ "Variable '"+str(w)+"' is not initialized before your WRITE statement.")

            
        
    """-----------------------------------------------------------------------------"""       
    """                              ADD OP                                           """
    """-----------------------------------------------------------------------------"""
    def add_op(self, op, mipsVar0, mipsVar1, lineNum): # why are we using mipsVar?
        #xprint("\t\tADDOP " + mipsVar0 + " " + op + " " + mipsVar1)
        # vars
        tempLoad = ""
        loadRec0 = ""                                                           # if we have a variable
        loadRec1 = ""                                                           # if we have two variables
        opLine   = ""                                                           # operation code with registers
        newVar   = ""                                                           # new variable declaration
        tab0 = ""
        tab1 = ""
        
        rec0 = self.getRecUsingMips(mipsVar0)
        #xprint("\t\tStarting rec0\t" + str(rec0.rType))
        rec1 = self.getRecUsingMips(mipsVar1)
        #xprint("\t\tStarting rec1\t" + str(rec1.rType))
        
        if(rec0 == False or rec1 == False):
            self.errMessage(str(lineNum) +": "+" Error: A variable in your expression is not initialized.")  
        elif(rec0.rType == "intID"):
            tempLoad = "\n" + "lw\t" + "$t0" + ",\t" + rec0.mipsVar             # loading variable
        elif(rec0.rType == "INTLITERAL"):
            tempLoad = "\n" + "li\t" + "$t0" + ",\t" + rec0.srcVar              # loading immediate
            tab0 = "\t"
        else:
            self.errMessage(str(lineNum) +": A variable in your expression is not an int.")
            
        loadRec0 = tempLoad                                                     # adding all together

        if(rec1.rType == "intID"):
            tempLoad = "lw\t"+ "$t1" + ",\t" + rec1.mipsVar                     # loading second term as variable
        elif(rec1.rType == "INTLITERAL"):
            tempLoad = "li\t" + "$t1" + ",\t" + rec1.srcVar                     # loading second term as immediate
            tab1="\t"
        else:
            self.errMessage(str(lineNum) +": "+" A variable in your expression is not an int.")
        loadRec1 = tempLoad                                                     # add them all together
        
        if(op == "+"):
            opLine = "add $t2,\t$t0,\t$t1"                                      # addition operation
        elif(op=="-"):
           opLine = "sub $t2,\t$t0,\t$t1"                                       # subtraction op
        newVar = "temp" + str(self.tempExpCount)                                # create the newVar name
        self.addData(newVar + ": \t" + ".word\t" + "-1")                        # add it to the data declarations
        self.addCode(loadRec0 + tab0 + rec0Comment)                # load into register record1
        self.addCode(loadRec1 + tab1 + rec1Comment)                # load into register record2
        self.addCode(opLine+ "\t\t# perform the op")                              # perform the operation
        self.addCode("sw" + "\t" + "$t2,\t" + newVar+ swComment)  # store the value into the new temp variable
        
        tempRecord = self.addToSymbolTable(None, "temp" + str(self.tempExpCount), "intID")
        self.tempExpCount+=1                                                    # increase the num of tempVariables
        return tempRecord

    """-----------------------------------------------------------------------------"""       
    """                              Mult OP                                      """
    """-------------------------------------------------------------------------"""
    def mult_op(self, op, mipsVar0, mipsVar1, lineNum): # why are we using mipsVar?
        # vars
        tempLoad  = ""
        loadRec0  = ""                                       # if we have a variable
        loadRec1  = ""                                       # if we have two variables
        opLine    = ""                                       # operation code with registers
        newVar    = ""                                       # new variable declaration
        hiLo = "mflo"
        tab0 = ""
        tab1 = ""
        rec0 = self.getRecUsingMips(mipsVar0)
        rec1 = self.getRecUsingMips(mipsVar1)
        #xprint("\t\t1: " + mipsVar0 + " 2: " + mipsVar1) 
        if(rec0 == False or rec1 == False):
            self.errMessage(str(lineNum) +": A variable in your expression is not initialized.")    
        elif(rec0.rType == "intID"):
            tempLoad = "\n" + "lw\t" + "$t0" + ",\t" + rec0.mipsVar # loading variable
        elif(rec0.rType == "INTLITERAL"):
            tempLoad = "\n" + "li\t" + "$t0" + ",\t" + rec0.srcVar  # loading immediate
            tab0 = "\t"
        else:
            self.errMessage(str(lineNum) +": "+ " A variable in your expression is not an int.")    


        loadRec0 = tempLoad                                          # adding all together
        #xprint("\t\ttype: " + rec1.rType)
        if(rec1.rType == "intID"):
            tempLoad = "lw\t"+ "$t1" + ",\t" + rec1.mipsVar         # loading second term as variable
        elif(rec1.rType == "INTLITERAL"):
            tempLoad = "li\t" + "$t1" + ",\t" + rec1.srcVar         # loading second term as immediate
            tab1 = "\t"
        else:
            self.errMessage(str(lineNum) +": "+"ERROR!! A variable in your expression is not an int.")
        loadRec1 = tempLoad                                         # add them all together
        
        if(op == "*"):
            opLine = "mult $t0,\t$t1"                               # mult operation
        elif(op=="/"):
           opLine = "div $t0,\t$t1"                                 # division op
        elif(op=="%"):
            opLine = "div $t0,\t$t1"                                 # mod op
            hiLo = "mfhi"
        newVar = "temp" + str(self.tempExpCount)                    # create the newVar name
        self.addData(newVar + ": \t" + ".word\t" + "-1" + multVarComment)            # add it to the data declarations
        self.addCode(loadRec0 + tab0+ rec0Comment)                    # load into register record1
        self.addCode(loadRec1 + tab1 + rec1Comment)                   # load into register record2
        self.addCode(opLine  + performOpComment)                          # perform the operation
        self.addCode(hiLo + "\t\t" + "$t0" + hiLoComment)                   # move from hi/lo
        self.addCode("sw" + "\t" + "$t0" + ",\t" + newVar + storeValComment)  # store the value into the new temp variable
        tempRecord = self.addToSymbolTable(None, "temp" + str(self.tempExpCount), "intID")
        self.tempExpCount+=1                                # increase the num of tempVariables
        return tempRecord

    """-----------------------------------------------------------------------------"""       
    """                              NUM OP                                         """
    """-----------------------------------------------------------------------------"""
    def num_op(self, op, mipsVar0, mipsVar1, lineNum):
        #xprint("\t\tNUMOP " + mipsVar0 + " " + op + " " + mipsVar1)
        # vars
        tempLoad = ""
        loadRec0 = ""                                                           # if we have a variable
        loadRec1 = ""                                                           # if we have two variables
        opLine   = ""                                                           # operation code with registers
        newVar   = ""                                                           # new variable declaration
        tab0 = ""
        tab1 = ""
        rec0 = self.getRecUsingMips(mipsVar0)
        #xprint("Starting rec0\t" + str(rec0.rType))
        rec1 = self.getRecUsingMips(mipsVar1)
        #xprint("Starting rec1\t" + str(rec1.rType))
        
        if(rec0 == False or rec1 == False):
            self.errMessage(str(lineNum) +": "+ "A variable in your expression is not initialized.")  
        elif(rec0.rType == "intID"):
            tempLoad = "\n" + "lw\t" + "$t0" + ",\t" + rec0.mipsVar             # loading variable
        elif(rec0.rType == "INTLITERAL"):
            tempLoad = "\n" + "li\t" + "$t0" + ",\t" + rec0.srcVar              # loading immediate
            tab0 = "\t"
        else:
            self.errMessage(str(lineNum) +": A variable in your expression is not an int.")
            
        loadRec0 = tempLoad                                                     # adding all together

        if(rec1.rType == "intID"):
            tempLoad = "lw\t"+ "$t1" + ",\t" + rec1.mipsVar                     # loading second term as variable
        elif(rec1.rType == "INTLITERAL"):
            tempLoad = "li\t" + "$t1" + ",\t" + rec1.srcVar                     # loading second term as immediate
            tab1="\t"
        else:
            self.errMessage(str(lineNum) +": A variable in your expression is not an int.")
        loadRec1 = tempLoad                                                     # add them all together


        # here we don't need to branch, we need to evaluate...
        if(op == "<="):
            # if is 
            opLine = "sle" + "\t" + "$t2" +",\t" + "$t0"+",\t" + "$t1 \t# <=" # less than equal
            
        elif(op==">="):
            opLine = "sge" + "\t" + "$t2" +",\t" + "$t0"+",\t" + "$t1 \t# >=" # greater than equal
        elif(op == "<"):
            opLine = "slt" + "\t" + "$t2" +",\t" + "$t0"+",\t" + "$t1 \t# <" # less than operation
        elif(op==">"):
            opLine = "sgt" + "\t" + "$t2" +",\t" + "$t0"+",\t" + "$t1 \t # >" # greater than op
        elif(op =="=="):
            opLine = "seq $t2,\t$t0,\t$t1 \t# =="                                      # equal op
        elif(op =="!="):
            opLine = "sne $t2,\t$t0,\t$t1 \t# !="  

        newVar = "bool" + str(self.boolCount)                                # create the newVar name            
        self.addData(newVar + ": \t" + ".word\t" + "-1")                        # add it to the data declarations
        self.addCode(loadRec0 + tab0 + rec0Comment)                 # load into register record1
        self.addCode(loadRec1 + tab1 + rec1Comment)                 # load into register record2
        self.addCode(opLine+ "\t\t# perform the op")                # perform the operation
        self.addCode("sw" + "\t" + "$t2,\t" + newVar+ swComment)  # store the value into the new temp variable
        tempRecord = self.addToSymbolTable(None, newVar, "boolID")
        self.boolCount+=1                                                    # increase the num of tempVariables
        return tempRecord

    """-----------------------------------------------------------------------------"""       
    """                              BOOL OP                                          """
    """-----------------------------------------------------------------------------"""
    def bool_op(self, op, mipsVar0, mipsVar1, lineNum):
        #xprint("\t\tBOOLOP \t" + mipsVar0 + " \t" + op + " \t" + mipsVar1)
        # vars
        tempLoad = ""
        loadRec0 = ""                                                           # if we have a variable
        loadRec1 = ""                                                           # if we have two variables
        opLine   = ""                                                           # operation code with registers
        newVar   = ""                                                           # new variable declaration
        tab0 = ""
        tab1 = ""
        rec0 = self.getRecUsingMips(mipsVar0)
        #xprint("Starting rec0\t" + str(rec0.rType))
        rec1 = self.getRecUsingMips(mipsVar1)
        #xprint("Starting rec1\t" + str(rec1.rType))
        
        if(rec0 == False or rec1 == False):
            self.errMessage(str(lineNum) +": A variable in your expression is not initialized.")  
        elif(rec0.rType == "boolID"):
            tempLoad = "\n" + "lw\t" + "$t0" + ",\t" + rec0.mipsVar             # loading variable
        elif(rec0.rType == "STRINGLITERAL"):
            if(rec1.srcVar == "True"):
                tempLoad = "li\t" + "$t1" + ",\t" + str(1)                    # loading second term as immediate
            elif(rec1.srcVar == "False"):
                tempLoad = "li\t" + "$t1" + ",\t" + str(0)                    # loading second term as immediate
            else:
                self.errMessage(str(lineNum) +": A variable in your expression is not a boolean.")
            tab1="\t"
        else:
            self.errMessage(str(lineNum) +": A variable in your expression is not a boolean.")
            
        loadRec0 = tempLoad                                                     # adding all together

        if(rec1.rType == "boolID"):
            tempLoad = "lw\t"+ "$t1" + ",\t" + rec1.mipsVar                     # loading second term as variable
        elif(rec1.rType == "STRINGLITERAL"):
            if(rec1.srcVar == "True"):
                tempLoad = "li\t" + "$t1" + ",\t" + str(1)                    # loading second term as immediate
            elif(rec1.srcVar == "False"):
                tempLoad = "li\t" + "$t1" + ",\t" + str(0)                    # loading second term as immediate
            else:
                self.errMessage(str(lineNum) +": ERROR!! You are not providing a boolean value.")
            tab1="\t"
        else:
            self.errMessage(str(lineNum) +": A variable in your expression is not a boolean.")
        loadRec1 = tempLoad                                                     # add them all together


        if(op == "or"):
            opLine = "or $t2,\t $t0, \t$t1"
        elif(op == "and"):
            opLine = "and $t2, \t$t0, \t$t1"

            

        newVar = "bool" + str(self.boolCount)                                # create the newVar name            
        self.addData(newVar + ": \t" + ".word\t" + "-1")                        # add it to the data declarations
        self.addCode(loadRec0 + tab0 + rec0Comment)                 # load into register record1
        self.addCode(loadRec1 + tab1 + rec1Comment)                 # load into register record2
        self.addCode(opLine+ "\t\t# perform the op")                # perform the operation
        self.addCode("sw" + "\t" + "$t2,\t" + newVar+ swComment)  # store the value into the new temp variable
        tempRecord = self.addToSymbolTable(None, newVar, "boolID")
        self.boolCount+=1                                                    # increase the num of tempVariables
        return tempRecord


    """-----------------------------------------------------------------------------"""       
    """                              PROCESS LITERAL                                """
    """-----------------------------------------------------------------------------"""
    def process_literal(self, srcVar, lineNum):
        #xprint("\t\tProcess Literal: " + srcVar)
        negative = ""
        if (str(srcVar)[0] == "-"):
            nagative = "neg_"
        mipsVar = negative + "mips" + srcVar
        if (int(srcVar)>32768):
            self.errMessage(str(lineNum) +": '"+str(srcVar)+"' is to long!.")
            sys.exit(0)
            #ERROR!!
        rec = self.getRecUsingSrc(srcVar)
        if (rec == False):
            rec = self.addToSymbolTable(srcVar, mipsVar, "INTLITERAL")
            #xself.printSymbolTable();
            self.addData(mipsVar+":\t" + ".word" + "\t" + srcVar)
        return rec;

    """-----------------------------------------------------------------------------"""       
    """                              PROCESS STRING LITERAL                         """
    """-----------------------------------------------------------------------------"""
    def process_string_literal(self, srcVar, lineNum):
        #xprint("\t\tProcess String Literal: " + srcVar)
        mipsVar = "mipsS" + str(self.stringLitCount)
        rec = self.getRecUsingSrc(srcVar)
        if (rec == False):
            rec = self.addToSymbolTable("\"" +srcVar + "\"", mipsVar, "STRINGLITERAL")
            #xself.printSymbolTable();
            self.addData(mipsVar+":\t" + ".asciiz" + "\t" + "\"" + srcVar + "\"")
            self.stringLitCount = self.stringLitCount +1
        return rec;

    """-----------------------------------------------------------------------------"""       
    """                              PROCESS BOOL LITERAL                           """
    """-----------------------------------------------------------------------------"""
    #################################### TO-DO ########################################
    def process_bool_literal(self, srcVar, lineNum):
        #xprint("\t\tProcess Bool Literal: " + srcVar)
        mipsVar = "mips" + srcVar
        rec = self.getRecUsingSrc(srcVar)
        if (rec == False):
            rec = self.addToSymbolTable(srcVar, mipsVar, "BOOLLITERAL")
            #xself.printSymbolTable();
            if(srcVar == "True"):
                self.addData(mipsVar+":\t" + ".word" + "\t" + str(1))
            elif(srcVar == "False"):
                self.addData(mipsVar+":\t" + ".word" + "\t" + str(0))
        if(srcVar =="False"):
            rec = self.getRecUsingMips("mipsFalse")
        elif(srcVar =="True"):
            rec = self.getRecUsingMips("mipsTrue")
        return rec;
    ###################################################################################

    """-----------------------------------------------------------------------------"""       
    """                              NEGATE TERM                                    """
    """-----------------------------------------------------------------------------"""
    def negate_term(self, mipsVar, lineNum):                     # by the time we get to negate_term, the value should
        # be in the fucking symbolTable
        #xprint("\t\tNEGATE " + mipsVar)
        rec = self.getRecUsingMips(mipsVar)
        if(rec == False):
            self.errMessage(str(lineNum) +": You did not provide a proper term for negation.")
        if(rec.mipsVar == "mipsTrue"):
            rec = self.getRecUsingMips("mipsFalse")
            #xprint("\t\tReturning " + rec.mipsVar)
            return rec
        elif(rec.mipsVar == "mipsFalse"):
            rec = self.getRecUsingMips("mipsTrue")
            #xprint("\t\tReturning " + rec.mipsVar)
            return rec
        elif(rec.mipsVar[:4] == "bool"):
            self.addCode("lw $t0, \t" + mipsVar)
            self.addCode("not $t1, \t$t0")
            newVar = "bool" + str(self.boolCount)                               # create the newVar name            
            self.addData(newVar + ": \t" + ".word\t" + "-1")                    # add it to the data declarations
            self.addCode("sw" + "\t" + "$t1,\t" + newVar+ swComment)            # store the value into the new temp variable
            tempRecord = self.addToSymbolTable(None, newVar, "boolID")
            self.boolCount+=1                                                    # increase the num of tempVariables
            return tempRecord

            rec = self.getRecUsingMips("mipsTrue")
            #xprint("\t\tReturning " + rec.mipsVar)
            return rec
        # i have a better idea...use add_op to create a negative term and return that...
        return self.add_op("-", "defZero", rec.mipsVar, lineNum)
    """-----------------------------------------------------------------------------"""       
    """                              PROCESS ID                                     """
    """-----------------------------------------------------------------------------"""
    def process_id(self, srcVar, addToTable):
        #xprint("\t\tProcess ID " + srcVar)
            
        rec = self.getRecUsingSrc(srcVar)                   # means check to see if already in the table  
        return rec;
    """-----------------------------------------------------------------------------"""       
    """                              DECLARE                                        """
    """-----------------------------------------------------------------------------"""
    def declare (self, srcVar, idType, lineNum):
        rec = self.getRecUsingSrc(srcVar)
        mipsVar = srcVar
        #xprint("\t\tDeclare: " + str(srcVar) + " " + str(idType))
        if (rec == False):           # if its not in table and we are supposed to add...  """and addToTable == True"""
            if (srcVar[:4] == "temp"):                      # 
                mipsVar = "mipsTemp" + srcVar[5:-1]
            rec = self.addToSymbolTable(srcVar, mipsVar, idType + "ID")
        else:
            self.errMessage(str(lineNum) +": Duplicate declaration")
        #xprint("\t\t" + self.symbolTable[0].mipsVar)
        mipsVar = self.getRecUsingSrc(srcVar)
        if (mipsVar.rType[-2:] == "ID"):                                # do this for IDs
            self.addData(mipsVar.mipsVar+":\t" + ".word" + "\t" + "-1") #
            #xprint("adding " + srcVar + " to data section" )
        return rec                                                  # else do nothing

    """-----------------------------------------------------------------------------"""       
    """                              If Start                                         """
    """-----------------------------------------------------------------------------"""
    def ifStart (self, record, lineNum):
        #xprint("\t\tstarting if " + str(varName.mipsVar))
        rec = record
        if(rec == False):
            self.errMessage(str(lineNum) +": Invalid boolean term given for condition.")
        self.addCode("lw" + "\t" + "$t0" + ",\t" + rec.mipsVar)
        self.addCode("beq" + "\t" + "$t0" + ",\t" + "0" + ",\t" + "elseStart" + str(self.elseCount))
        self.addCode("\nifStart" + str(self.ifCount) + ":")
        count = self.ifCount
        self.ifCount+=1
        return count


    """-----------------------------------------------------------------------------"""       
    """                              Else Start                                       """
    """-----------------------------------------------------------------------------"""
    def elseStart (self, count, lineNum):
        self.addCode("jal" + "\tafterIfCount" + str(count)) # jump to end if
        self.addCode("\nelseStart" + str(count) + ":")
        self.afterIfCount = count
        #self.elseCount+=1

    """-----------------------------------------------------------------------------"""       
    """                              End If                                           """
    """-----------------------------------------------------------------------------"""
    def endIf (self, lineNum):
        self.addCode("\nafterIfCount" + str(self.afterIfCount) + ":")
        #self.afterIfCount+=1

    """-----------------------------------------------------------------------------"""       
    """                              WHILE START                                      """
    """-----------------------------------------------------------------------------"""
    def whileLabel (self, lineNum):
        self.addCode("\nwhileStart" + str(self.whileStartCount) + ":")
        count = self.whileStartCount;
        self.whileStartCount+=1
        return count

    def whileStart (self, varName, count, lineNum):
        rec = varName
        self.addCode("lw" + "\t" + "$t0" + ",\t" + rec.mipsVar)
        self.addCode("beq" + "\t" + "$t0" + ",\t" + "0" + ",\t" + "whileEnd" + str(count))

    """-----------------------------------------------------------------------------"""       
    """                              WHILE END                                        """
    """-----------------------------------------------------------------------------"""
    def whileEnd (self, count, lineNum):
        self.addCode("jal" + "\twhileStart" + str(count)) # jump to while Start
        #self.addCode("jal" + "\twhileStart" + str(self.whileStartCount-1)) # jump to while Start
        self.addCode("\nwhileEnd" + str(count) + ":")
        self.whileEndCount+=1
    ###                              END GEN METHODS                                ###
    ###################################################################################
    ###                                                                             ###
    ###################################################################################
    ###                              HELPER METHODS                                 ###

    def addData(self, code):
        self.fileData = self.fileData + "\n" + code

    def addCode(self, code):
        self.fileCode = self.fileCode + "\n" + code

    def addMethod(self, val1, val2):
        self.testMethod()

    def writeFile(self):
        print(self.fileContents)
        fo = open(self.outFile, "wb")
        fo.write(bytes(self.fileContents, 'UTF-8'))
        fo.close()

    def errMessage(self, error):
        print("Error on line " + error) # for web display
        sys.exit("Error on line " + error)
    ###                              END HELPER METHODS                             ###
    ###################################################################################
    ###                                                                             ###
    ###################################################################################
    ###                              SYMBOL TABLE                                   ###

    # Add params to the symbol table
    def addToSymbolTable(self, srcVar, mipsVar, rType):
        rec = Record(srcVar, mipsVar, rType)
        self.symbolTable.append(rec);
        return rec

    # Get a rec from the symbol table using srcVar
    def getRecUsingSrc(self, srcVar):
        for rec in self.symbolTable:
            if rec.srcVar == srcVar:
                return rec;
        return False;
    
    # Get a rec from the symbol table using mipsVar
    def getRecUsingMips(self, mipsVar):
        for rec in self.symbolTable:
            if rec.mipsVar == mipsVar:
                return rec;
        return False;

    #def printRecord(self, rec, index = 0):
        #xprint("\t\t" + str(index) + ": " +str(rec.srcVar) + ",\t"+str(rec.mipsVar), ",\t"+str(rec.rType))
    #def printSymbolTable(self):
        #for idx, rec in enumerate(self.symbolTable):
            #xself.printRecord(rec, idx)
            ##xprint()
