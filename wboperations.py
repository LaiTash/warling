__author__ = 'Lai Tash (lai.tash@yandex.ru)'
import header_operations as headers
import warling_specific_ops as spec_headers


opcodes = [None for i in xrange(5000)]
ops = vars(headers)
ops.update(vars(spec_headers))

def operation(func):
    opcodes[ops[func.__name__]] = func
    return func

#region Output and debugging

@operation
def display_message(machine, s):
    print s


@operation
def output_int(machine, v):
    print machine.get_int(v)

#endregion

#region Integer math

@operation
def store_add(machine, destination, *operands):
    destination = machine.parse_int(destination)
    result = sum((machine.get_int(x) for x in operands))
    destination.set(result)

@operation
def val_add(machine, destination, *operands):
    destination = machine.parse_int(destination)
    result = sum((machine.get_int(x) for x in operands))
    destination.add(result)

#endregion

#region Integer comparsions

@operation
def eq(machine, value1, value2):
    value1 = machine.get_int(value1)
    value2 = machine.get_int(value2)
    if value1 != value2:
        machine.signal_break()

#endregion


#opcodes[headers.display_message] = output
#opcodes[headers.store_add] = store_add
#opcodes[spec_headers.output_int] = output_int