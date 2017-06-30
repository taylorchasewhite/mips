
.data
prompt:	.asciiz	"Please provide an integer value: "
newLine:	.asciiz	"\n"
defZero:	.word	0
mipsSTrue:	.asciiz	"True"
mipsSFalse:	.asciiz	"False"
mipsTrue:	.word	1
mipsFalse:	.word	0
bool0: 	.word	-1

.text

lw	$t0,	mipsTrue			# load into register record0
lw	$t1,	mipsTrue			# load into register record1
or $t2,	 $t0, 	$t1		# perform the op
sw	$t2,	bool0			# store into newVar

la	$a0,		newLine
li	$v0,	4
syscall						# print out

lw	$t0,	bool0
jal writeTrue
li	$v0,	4
syscall						# print out

li	$v0,	10
syscall						# exit

writeTrue:
move $s0, $ra
la $t2, mipsSTrue

la	$a0,	mipsSTrue				# load into $a0
beq $t0, 0, writeFalse
jr $s0
writeFalse:
la $t2, mipsSFalse

la	$a0,	mipsSFalse				# load into $a0
jr $s0