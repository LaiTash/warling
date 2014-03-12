__author__ = 'Lai Tash (lai.tash@yandex.ru)'


from itertools import repeat
from collections import deque, defaultdict, namedtuple
from abc import ABCMeta, abstractmethod

#region constants
OPC_ENDTRY = 3
OPC_TRYBEGIN = 4
OPC_ELSETRY = 5
OPC_TRYFORRANGE = 6
OPC_TRYFORRANGE_BACK = 7
OPC_BLOCK = (OPC_TRYBEGIN, OPC_TRYFORRANGE, OPC_TRYFORRANGE_BACK)

TAG_REGISTER = 1
OP_NUM_VALUE_BITS = 56
OPMASK_REGISTER = TAG_REGISTER << OP_NUM_VALUE_BITS

OTYPE_PLAIN = 0
OTYPE_INT_REG = 1

BT_PLAIN = 0
BT_TRY = 1
BT_TRYFORWARD = 2
BT_TRYBACK = 3
BT_SCRIPT  = 4
BT_HAS_ENDTRY = (BT_TRY, BT_TRYBACK, BT_TRYFORWARD)
#endregion

class WBScript(object):
    """
    The simple script code container
    """
    def __init__(self, name, code):
        """
        name - a script name
        code - code of the script
        """
        self.name = name
        self.code = code


class WBError(Exception):
    def __init__(self, script, operation, description):
        super(Exception, self).__init__()
        self.script = script
        self.operation = operation
        self.description = description

    def __str__(self):
        return "(at script '%s', operation %i: %s" % (self.script, self.operation, self.description)


#region virtual machine memory
class WBMemorySlot(object):
    __metaclass__ = ABCMeta

    def __init__(self, machine):
        self.machine = machine

    @abstractmethod
    def set(self, value):
        pass

    @abstractmethod
    def get(self):
        pass

class WBMemoryIntSlot(WBMemorySlot):
    def add(self, value):
        self.set(self.get() + value)

    def inc(self):
        self.add(1)

    def __int__(self):
        return self.get()

    def ensure_value(self, value):
        if type(value) is not int:
            self.machine.error('integer expected')

class WBIntConstant(WBMemoryIntSlot):
    def __init__(self, machine, value):
        super(WBMemoryIntSlot, self).__init__(machine)
        self.ensure_value(value)
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.machine.error("can't assign to constant")

class WBIntRegister(WBMemoryIntSlot):
    def __init__(self, machine, register):
        super(WBIntRegister, self).__init__(machine)
        self.register = register
        if register < 0 or register >= len(machine.global_state.int_registers):
            machine.error("no such register")

    def set(self, value):
        self.ensure_value(value)
        self.machine.global_state.int_registers[self.register] = value


    def get(self):
        return self.machine.global_state.int_registers[self.register]


class WBIntGlobal(WBMemoryIntSlot):
    def __init__(self, machine, name):
        super(WBIntGlobal, self).__init__(machine)
        self.name = name

    def set(self, value):
        self.ensure_value(value)
        self.machine.global_state.int_variables[self.name] = value

    def get(self, value):
        return self.machine.global_state.int_variables[self.name]

class WBIntLocal(WBMemoryIntSlot):
    def __init__(self, machine, name):
        super(WBIntLocal, self).__init__(machine)
        self.name = name

    def set(self, value):
        self.ensure_value(value)
        self.machine.script_state.int_variables[self.name] = value

    def get(self):
        return self.machine.script_state.int_variables[self.name]
#endregion

class ValueContainer(object):
    def __init__(self):
        for field in self.__class__.fields:
            setattr(self, field, None)

    def copy(self):
        result = self.__class__()
        for field in self.__class__.fields:
            setattr(result, field, getattr(self, field))
        return result

class ValueContainerMeta(type):
    def __new__(cls, name, fields):
        #scls.__name__ = name
        #cls.fields = fields
        dct = dict(zip(fields, repeat(None, len(fields))))
        dct.update({"fields": fields})
        return type(name, (ValueContainer,), dct)


class WBMachine(object):
    machine = None
    Error = WBError


    #region Initialisation

    def __init__(self, scripts, opcodes, int_registers = 99, flt_registers = 99, str_registers = 99):
        """
        scripts - a [name, WBScript] defaultdict
        int_registers - number of integer registers
        flt_registers - number of floating point registers
        str_registers - number of string registers
        """
        self.global_state = ValueContainerMeta('WBGlobalState', [
            'int_registers',
            'flt_registers',
            'str_registers',
            'scripts',
            'int_variables'
        ])()
        self.script_state = ValueContainerMeta('WBScriptState', [
            'script',
            'arguments',
            'int_variables',
        ])()
        self.execution_state = ValueContainerMeta('WBExecutionState', [
            'head',
            'opcode',
            'arguments',
            'operation'
        ])()
        self.block_state = ValueContainerMeta('WBLocalState', [
            'type',
            'start_position',
            'end_position',
            'iterator',
            'sig_break',
        ])()
        self.init_global_state(scripts, int_registers, flt_registers, str_registers)
        self.opcodes = opcodes


    def init_global_state(self, scripts, int_registers, flt_registers, str_registers):
        self.global_state.scripts = scripts
        self.global_state.int_registers = list(repeat(0, int_registers))
        self.global_state.flt_registers = list(repeat(0.0, flt_registers))
        self.global_state.str_registers = list(repeat("", str_registers))
        self.global_state.int_variables = defaultdict(lambda: 0)

    #endregion

    #region Operations on variables
    def get_int(self, value):
        return self.parse_int(value).get()

    def parse_int(self, value):
        if type(value) is str:
            if len(value) < 2:
                self.error("incorrect value")
            if value[0] == ":":
                name = value[1:]
                return WBIntLocal(self, name)
            elif value[0] == "@":
                name = value[1:]
                return WBIntGlobal(self, name)
        elif type(value) is int:
            if value & OPMASK_REGISTER:
                return WBIntRegister(self, value ^ OPMASK_REGISTER)
            else:
                return WBIntConstant(self, value)
        else:
            self.error("incorrect value")
    #endregion

    #region head manipulation
    def goto(self, position):
        self.execution_state.head = position
        if self.execution_state.head >= len(self.code):
            if self.block_state.type != BT_SCRIPT:
                self.error("head outside script code")
            else:
                return
        self.execution_state.operation = self.code[self.execution_state.head]
        if type(self.execution_state.operation) is int:
            self.execution_state.opcode = self.execution_state.operation
            self.execution_state.arguments = tuple()
        else:
            self.execution_state.opcode = self.execution_state.operation[0]
            self.execution_state.arguments = self.execution_state.operation[1:]

    def head_forward(self):
        self.goto(self.execution_state.head + 1)

    def head_back(self):
        self.goto(self.execution_state.head - 1)

    def next_operation(self):
        self.execute_operation()
        self.head_forward()

    def skip_to(self, *opcodes):
        opcode = self.execution_state.opcode
        while True:
            opcode = self.execution_state.opcode
            if opcode in OPC_BLOCK:
                self.head_forward()
                self.skip_after(OPC_ENDTRY)
            elif opcode not in opcodes:
                self.head_forward()
            else:
                break


    def skip_after(self, *opcodes):
        self.skip_to(*opcodes)
        self.head_forward()
    #endregion

    #region operation execution
    def execute_script_code(self):
        while self.execution_state.head < len(self.code) and not self.block_state.sig_break:
            self.next_operation()

    def execute_operation(self):
        opcode = self.execution_state.opcode
        if opcode == OPC_TRYBEGIN:
            self.execute_else()
        elif opcode == OPC_ELSETRY and self.block_state.type != BT_TRY:
            self.error("else_try outside begin_try")
        elif opcode == OPC_ENDTRY and self.block_state.type not in BT_HAS_ENDTRY:
            self.error("end_try outside try block")
        elif opcode in (OPC_TRYFORRANGE, OPC_TRYFORRANGE_BACK):
            self.execute_try_range()
        else:
            self.execute_plain()
    #endregion

    #region block management
    def init_block(self, block_type):
        self.block_state.type = block_type
        self.block_state.sig_break = False
        self.block_state.start_position = self.execution_state.head
        self.block_state.end_position = None

    def quit_block(self):
        if self.block_state.end_position is None:
            self.skip_to(OPC_ENDTRY)
        else:
            self.goto(self.block_state.end_position)


    def execute_else(self):
        old_block = self.block_state.copy()
        self.init_block(BT_TRY)
        self.head_forward()
        while self.execution_state.opcode not in (OPC_ELSETRY, OPC_ENDTRY):
            self.next_operation()
            if self.block_state.sig_break: # there was a break
                self.skip_to(OPC_ELSETRY, OPC_ENDTRY)
                if self.execution_state.opcode == OPC_ELSETRY: # we have an Else, go there and continue working
                    self.block_state.sig_break = False
                    self.head_forward()
                else: # there's no more Else's, quit
                    break
            elif self.execution_state.opcode == OPC_ELSETRY: # we've reached Else and there was no break, quit
                self.skip_to(OPC_ENDTRY)
                break
            elif self.execution_state == OPC_ENDTRY: # we've reached End with no break, quit
                break

        self.block_state = old_block

    def execute_try_range_strict(self):
        old_block = self.block_state.copy()
        forward = self.execution_state.opcode == OPC_TRYFORRANGE
        self.init_block(BT_TRYFORWARD if forward else BT_TRYBACK)
        self.block_state.iterator = self.parse_int(self.execution_state.arguments[0])
        try_from = self.get_int(self.execution_state.arguments[1])
        try_to = self.get_int(self.execution_state.arguments[2])
        iteration = xrange(try_from, try_to, int(forward) or -1)
        for i in iteration:
            self.block_state.sig_break = False
            self.goto(self.block_state.start_position + 1)
            self.block_state.iterator.set(i)
            while self.execution_state.opcode != OPC_ENDTRY:# and not self.block_state.sig_break:
                self.next_operation()
                if self.block_state.sig_break:
                    break
        self.quit_block()
        self.block_state = old_block

    def execute_try_range_nostrict(self):
        old_block = self.block_state.copy()
        forward = self.execution_state.opcode == OPC_TRYFORRANGE
        direction = int(forward) or -1
        self.init_block(BT_TRYFORWARD if forward else BT_TRYBACK)
        self.block_state.iterator = self.parse_int(self.execution_state.arguments[0])
        try_from = self.get_int(self.execution_state.arguments[1])
        try_to = self.get_int(self.execution_state.arguments[2])
        self.block_state.iterator.set(try_from)
        #while (self.block_state.iterator.get() < try_to) if forward else (self.block_state.iterator.get() > try_to):
        ttd = try_to * direction
        while (self.block_state.iterator.get() * direction < ttd): # i liek it this way!
            self.block_state.sig_break = False
            self.goto(self.block_state.start_position + 1)
            self.block_state.iterator.add(direction)
            while self.execution_state.opcode != OPC_ENDTRY:# and not self.block_state.sig_break:
                self.next_operation()
                if self.block_state.sig_break:
                    break
        self.quit_block()
        self.block_state = old_block

    execute_try_range = execute_try_range_strict


    def execute_plain(self):
        function = self.opcodes[self.execution_state.opcode]
        if function is None:
            self.error("opcode %i has no function" % self.execution_state.opcode)
        apply(function, (self,) + self.execution_state.arguments)


    #endregion

    #region support functions and properties

    @property
    def code(self):
        return self.script_state.script.code

    def error(self, description):
        raise WBMachine.Error(
            self.script_state.script.name,
            self.execution_state.head,
            description
        )

    def signal_break(self):
        self.block_state.sig_break = True

    #endregion

    def execute(self, script_name, arguments):
        old_script_state = self.script_state.copy()
        old_execution_state = self.execution_state.copy()
        old_block_state = self.block_state.copy()
        self.script_state.script = self.global_state.scripts[script_name]
        if self.script_state.script is None:
            self.error("script '%s' does not exist" % script_name)
        self.script_state.int_variables = defaultdict(lambda: 0)
        self.block_state.start_position = 0
        self.block_state.sig_break = False
        self.block_state.type = BT_SCRIPT
        self.script_state.arguments = (self.get_int(value) for value in arguments)
        self.goto(0)
        self.execute_script_code()




