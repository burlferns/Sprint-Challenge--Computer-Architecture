"""CPU functionality."""
import sys

###########################
# Command opcodes
###########################
ADD = 0b10100000 # add regA & regB, store in regA --- ADD regA regB
CALL = 0b01010000 # call subroutine at address --- CALL register
CMP = 0b10100111 # compare register values --- CMP regA regB
HLT = 0b00000001 # halt & exit --- HLT
JEQ = 0b01010101 # if E flag true jmp to reg --- JEQ register
JNE = 0b01010110 # if E flag false jmp to reg --- JNE register
JMP = 0b01010100 # jump to addr in reg --- JMP register
LDI = 0b10000010 # load register immediate --- LDI register integer
MUL = 0b10100010 # multiply regA & regB, store in regA --- MUL regA regB
POP = 0b01000110 # pop stack into register --- POP register
PRN = 0b01000111 # print register contents --- PRN register
PUSH = 0b01000101 # push into stack register contents --- PUSH register
RET = 0b00010001 # return from subroutine --- RET
##########################

# SP is the general purpose register index for the stack pointer 
SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xF4
        self.pc = 0 # program counter
        self.fl = 0 # flags register 00000LGE
        self.ir = 0 # instruction register
        self.running = True
        self.branchtable = {}
        self.branchtable[ADD] = self.handle_ADD
        self.branchtable[CALL] = self.handle_CALL
        self.branchtable[CMP] = self.handle_CMP
        self.branchtable[HLT] = self.handle_HLT
        self.branchtable[JEQ] = self.handle_JEQ
        self.branchtable[JNE] = self.handle_JNE
        self.branchtable[JMP] = self.handle_JMP
        self.branchtable[LDI] = self.handle_LDI
        self.branchtable[MUL] = self.handle_MUL
        self.branchtable[POP] = self.handle_POP
        self.branchtable[PRN] = self.handle_PRN
        self.branchtable[PUSH] = self.handle_PUSH
        self.branchtable[RET] = self.handle_RET

    def handle_ADD(self):
        regA_addr = self.ram_read(self.pc+1)
        regB_addr = self.ram_read(self.pc+2)
        self.alu("ADD",regA_addr,regB_addr)

    def handle_CALL(self):
        reg_addr = self.ram_read(self.pc+1)
        addrForStack = self.pc+2
        self.pushStack(addrForStack)
        return self.reg[reg_addr]

    def handle_CMP(self):
        regA_addr = self.ram_read(self.pc+1)
        regB_addr = self.ram_read(self.pc+2)
        self.alu("CMP",regA_addr,regB_addr)

    def handle_HLT(self):
        self.running = False

    def handle_JEQ(self):
        if self.fl == 0b00000001:
            reg_addr = self.ram_read(self.pc+1)
            return self.reg[reg_addr]

    def handle_JNE(self):
        if (self.fl == 0b00000100) or (self.fl == 0b00000010):
            reg_addr = self.ram_read(self.pc+1)
            return self.reg[reg_addr]

    def handle_JMP(self):
        reg_addr = self.ram_read(self.pc+1)
        return self.reg[reg_addr]

    def handle_LDI(self):
        reg_addr = self.ram_read(self.pc+1)
        value = self.ram_read(self.pc+2)
        self.reg[reg_addr] = value

    def handle_MUL(self):
        regA_addr = self.ram_read(self.pc+1)
        regB_addr = self.ram_read(self.pc+2)
        self.alu("MUL",regA_addr,regB_addr)

    def handle_POP(self):
        reg_addr = self.ram_read(self.pc+1)
        value = self.popStack()
        self.reg[reg_addr] = value

    def handle_PRN(self):
        reg_addr = self.ram_read(self.pc+1)
        value = self.reg[reg_addr]
        print(value)

    def handle_PUSH(self):
        reg_addr = self.ram_read(self.pc+1)
        value = self.reg[reg_addr]
        self.pushStack(value)

    def handle_RET(self):
        return self.popStack()
    
    def popStack(self):
        value = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        return value

    def pushStack(self,value):
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP],value)


    def load(self,program):
        """Load a program into memory."""
        address = 0

        # For now, we've just hardcoded a program:
        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def ram_read(self,mar):
        return self.ram[mar]

    def ram_write(self,mar,mdr):
        self.ram[mar] = mdr


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b] 
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            else: 
                self.fl = 0b00000001
        #elif op == "SUB": etc
        else:
            raise Exception(f"Unsupported ALU operation: {op}")

        # By bitwise ANDing to 0xFF, the bits higher than 8 bits are 
        # chopped off from the add/multiply/etc result as it would be in
        # an actual CPU with an 8 bit ALU
        self.reg[reg_a] = self.reg[reg_a] & 0xFF


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print(f" | %02X " % (self.ram_read(self.reg[SP])), end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            self.ir = self.ram_read(self.pc)

            # self.trace()

            if self.ir in self.branchtable:
                pc_value = self.branchtable[self.ir]()
                if pc_value == None:
                    inst_len = ((self.ir & 0b11000000) >> 6) + 1
                    self.pc += inst_len
                else:
                    self.pc = pc_value
            else:
                print(f"Unknown instruction : {self.ir:>08b}")
                self.running = False

            
