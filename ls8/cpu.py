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
        self.running = False
        self.branch_table = {
            f"{0b10000010}": self.LDI,
            f"{0b01000111}": self.PRN,
            f"{0b10100010}": self.MUL,
            f"{0b01000101}": self.PUSH,
            f"{0b01000110}": self.POP,
            f"{0b01010000}": self.CALL,
            # f"{0b01010100}": self.JMP,
            f"{0b00010001}": self.RET,
            f"{0b10100000}": self.ADD,
            f"{0b00000001}": self.HLT,
        }

    def LDI(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg_write(operand_a, operand_b)
        self.pc = self.pc + 3

    def PRN(self):
        operand_a = self.ram_read(self.pc + 1)
        print(self.reg_read(operand_a))
        self.pc = self.pc + 2

    def ADD(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("ADD", operand_a, operand_b)
        self.pc = self.pc + 3

    def MUL(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.alu("MUL", operand_a, operand_b)
        self.pc = self.pc + 3

    def PUSH(self):
        operand_a = self.ram_read(self.pc + 1)
        self.sp = self.sp - 1
        self.ram_write(self.sp, self.reg_read(operand_a))
        self.pc = self.pc + 2

    def POP(self):
        operand_a = self.ram_read(self.pc + 1)
        stack_apex = self.ram_read(self.sp)
        self.reg_write(operand_a, stack_apex)
        self.sp = self.sp + 1
        self.pc = self.pc + 2

    def CALL(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.pc + 2
        self.ram_write(self.sp, operand_b)
        self.pc = self.reg_read(operand_a)

    def RET(self):
        self.pc = self.ram_read(self.sp)
        self.sp = self.sp + 1
        pass

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
            command = self.ram[self.pc]
            # print(command)
            self.branch_table[f"{command}"]()
