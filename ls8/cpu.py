"""CPU functionality."""
# this file resembles a model of a cpu and it's basic functionalities / characteristics

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.sp = self.reg[7]
        self.pc = 0
        self.fl = 0b00000000  # 0000000LGE
        self.opcode = self.ram_read(self.pc)
        self.operand_a = self.ram_read(self.pc + 1)
        self.operand_b = self.ram_read(self.pc + 2)
        self.running = False
        self.branch_table = {
            f"{0b10000010}": self.LDI,
            f"{0b01000111}": self.PRN,
            f"{0b10100000}": self.ADD,
            f"{0b10100111}": self.CMP,
            f"{0b10100010}": self.MUL,
            f"{0b10000100}": self.ST,
            f"{0b01000101}": self.PUSH,
            f"{0b01000110}": self.POP,
            f"{0b01010000}": self.CALL,
            f"{0b01010100}": self.JMP,
            f"{0b01010101}": self.JEQ,
            f"{0b01010110}": self.JNE,
            f"{0b00010001}": self.RET,
            f"{0b00000001}": self.HLT,
        }

    def LDI(self):
        self.reg_write(self.operand_a, self.operand_b)
        self.pc = self.pc + 3

    def PRN(self):
        print(self.reg_read(self.operand_a))
        self.pc = self.pc + 2

    def ADD(self):
        self.alu("ADD", self.operand_a, self.operand_b)
        self.pc = self.pc + 3

    def MUL(self):
        self.alu("MUL", self.operand_a, self.operand_b)
        self.pc = self.pc + 3

    def CMP(self):
        self.alu("CMP", self.operand_a, self.operand_b)
        self.pc = self.pc + 3

    def PUSH(self):
        self.sp = self.sp - 1
        self.ram_write(self.sp, self.reg_read(self.operand_a))
        self.pc = self.pc + 2

    def POP(self):
        stack_apex = self.ram_read(self.sp)
        self.reg_write(self.operand_a, stack_apex)
        self.sp = self.sp + 1
        self.pc = self.pc + 2

    def ST(self):
        self.ram_write(self.operand_a, self.operand_b)
        self.pc = self.pc + 3

    def CALL(self):
        return_address = self.pc + 2
        self.ram_write(self.sp, return_address)
        self.pc = self.reg_read(self.operand_a)

    def JMP(self):
        self.pc = self.reg_read(self.operand_a)

    def JEQ(self):
        if self.fl == 0b00000001:
            self.pc = self.reg_read(self.operand_a)
        else:
            self.pc = self.pc + 2

    def JNE(self):
        if self.fl != 0b00000001:
            self.pc = self.reg_read(self.operand_a)
        else:
            self.pc = self.pc + 2

    def RET(self):
        self.pc = self.ram_read(self.sp)
        self.sp = self.sp + 1

    def HLT(self):
        self.running = False

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def reg_read(self, register):
        return self.reg[register]

    def reg_write(self, register, value):
        self.reg[register] = value

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print(f"usage: {sys.argv[0]} filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                address = 0

                for line in f:
                    instruction = line.split("\n", 1)[0]
                    instruction = instruction.split("#", 1)[0]

                    if instruction.strip() == '':  # ignore comment-only lines
                        continue

                    self.ram_write(address, int(instruction, 2))
                    address += 1
            f.close()
        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == 'CMP':
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True

        while self.running:
            self.opcode = self.ram_read(self.pc)
            self.operand_a = self.ram_read(self.pc + 1)
            self.operand_b = self.ram_read(self.pc + 2)
            self.branch_table[f"{self.opcode}"]()
