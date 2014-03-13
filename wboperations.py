__author__ = 'Lai Tash (lai.tash@yandex.ru)'
import header_operations as headers
import warling_specific_ops as spec_headers


opcodes = [None for i in xrange(5000)]
ops = vars(headers)
ops.update(vars(spec_headers))

def operation(func):
    opcodes[ops[func.__name__]] = func
    return func

#region script handling
@operation
def call_script(machine, script_id, *operands):
    return machine.execute_script_by_index(machine.get_int(script_id), tuple(machine.get_int(op) for op in operands))

@operation
def store_script_param(machine, variable_name, parameter_index):
    variable = machine.parse_int(variable_name)
    if parameter_index < 0 or parameter_index > len(machine.script_state.arguments):
        machine.error("incorrect script parameter index")
    variable.set(machine.script_state.arguments[parameter_index-1])
#endregion

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
    return value1 == value2


#endregion


#opcodes[headers.display_message] = output
#opcodes[headers.store_add] = store_add
#opcodes[spec_headers.output_int] = output_int