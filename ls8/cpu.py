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
            f"{0b10000010}": self.opcode_LDI,
            f"{0b01000111}": self.opcode_PRN,
            f"{0b10100010}": self.opcode_MUL,
            f"{0b01000101}": self.opcode_PUSH,
            f"{0b01000110}": self.opcode_POP,
            f"{0b01010000}": self.opcode_CALL,
            f"{0b01010100}": self.opcode_JMP,
            f"{0b10100000}": self.opcode_ADD,
            f"{0b00000001}": self.opcode_HLT,
        }

    def opcode_LDI(self):
        self.LDI(self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc = self.pc + 3

    def opcode_PRN(self):
        self.PRN(self.ram_read(self.pc + 1))
        self.pc = self.pc + 2

    def opcode_ADD(self):
        self.alu("ADD", self.ram_read(self.pc + 1),
                 self.ram_read(self.pc + 2))
        self.pc = self.pc + 3

    def opcode_MUL(self):
        self.alu("MUL", self.ram_read(self.pc + 1),
                 self.ram_read(self.pc + 2))
        self.pc = self.pc + 3

    def opcode_PUSH(self):
        self.PUSH(self.ram_read(self.pc + 1))
        self.pc = self.pc + 2

    def opcode_POP(self):
        self.POP(self.ram_read(self.pc + 1))
        self.pc = self.pc + 2

    def opcode_CALL(self):
        self.CALL(self.ram_read(self.pc + 1))
        self.pc = self.ram[self.sp]

    def opcode_JMP(self):
        self.JMP(self.ram_read(self.pc + 1))

    def opcode_HLT(self):
        self.running = False

    def ram_read(self, index):
        return self.ram[index]

    def ram_write(self, index, value):
        self.ram[index] = value

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

    def LDI(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def PRN(self, index):
        print(self.reg[index])

    def PUSH(self, operand_a):
        self.sp = self.sp - 1
        self.ram[self.sp] = self.reg[operand_a]

    def POP(self, operand_a):
        self.LDI(operand_a, self.ram[self.sp])
        self.ram[self.sp] = 0b00000000
        self.sp = self.sp + 1

    def CALL(self, operand_a):
        # self.PUSH(self.pc + 2)
        # self.sp = self.sp - 1
        # self.ram[self.sp] = self.pc + 2
        self.pc = self.reg[operand_a]
        command = self.ram[self.pc]
        self.branch_table[f"{command}"]()

    def JMP(self, operand_a):
        self.pc = self.reg[operand_a]

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
