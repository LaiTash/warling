__author__ = 'Lai Tash (lai.tash@yandex.ru)'
from itertools import repeat


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


WBGlobalState = ValueContainerMeta('WBGlobalState', [
            'int_registers',
            'flt_registers',
            'str_registers',
            'scripts',
            'script_indices',
            'int_variables'
        ])

WBScriptState = ValueContainerMeta('WBScriptState', [
            'script',
            'arguments',
            'int_variables',
        ])

WBExecutionState = ValueContainerMeta('WBExecutionState', [
            'head',
            'opcode',
            'arguments',
            'operation'
        ])

WBLocalState = ValueContainerMeta('WBLocalState', [
            'type',
            'start_position',
            'end_position',
            'iterator',
            'sig_break',
        ])