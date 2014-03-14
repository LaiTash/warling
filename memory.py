from abc import ABCMeta, abstractmethod

__author__ = 'Lai Tash (lai.tash@yandex.ru)'

class WBMemorySlot(object):
    """
    Base class for accessing and manipulating the machine's memory
    """
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
    """
    Integer memory objects base class
    """
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
    """
    Integer constant
    """
    def __init__(self, machine, value):
        super(WBMemoryIntSlot, self).__init__(machine)
        self.ensure_value(value)
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.machine.error("can't assign to constant")


class WBIntRegister(WBMemoryIntSlot):
    """
    Integer register, representing reg0, reg1, etc
    """
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
    """
    Global integer variable ("@variablename")
    """
    def __init__(self, machine, name):
        super(WBIntGlobal, self).__init__(machine)
        self.name = name

    def set(self, value):
        self.ensure_value(value)
        self.machine.global_state.int_variables[self.name] = value

    def get(self, value):
        return self.machine.global_state.int_variables[self.name]


class WBIntLocal(WBMemoryIntSlot):
    """
    Local integer variable (":variablename")
    """
    def __init__(self, machine, name):
        super(WBIntLocal, self).__init__(machine)
        self.name = name

    def set(self, value):
        self.ensure_value(value)
        self.machine.script_state.int_variables[self.name] = value

    def get(self):
        return self.machine.script_state.int_variables[self.name]
