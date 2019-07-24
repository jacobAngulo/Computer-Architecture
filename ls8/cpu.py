"""CPU functionality."""
# this file resembles a model of a cpu and it's basic functionalities / characteristics

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0b00000000] * 256
        self.reg = [0b00000000] * 8
        self.pc = 0
        self.running = True
        self.branch_table = {
            f"{0b10000010}": self.handle_0b10000010,
            f"{0b01000111}": self.handle_0b01000111,
            f"{0b10100010}": self.handle_0b10100010,
            f"{0b00000001}": self.handle_0b00000001,
        }

    def handle_0b10000010(self):
        self.LDI(self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc = self.pc + 3

    def handle_0b01000111(self):
        self.PRN(self.ram_read(self.pc + 1))
        self.pc = self.pc + 2

    def handle_0b10100010(self):
        self.alu("MUL", self.ram_read(self.pc + 1),
                 self.ram_read(self.pc + 2))
        self.pc = self.pc + 3

    def handle_0b00000001(self):
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

    def LDI(self, register, value):
        self.reg[register] = value

    def PRN(self, index):
        print(self.reg[index])

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

        while self.running:
            command = self.ram[self.pc]
            self.branch_table[f"{command}"]()
