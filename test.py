__author__ = 'Lai Tash (lai.tash@yandex.ru)'
from header_operations import *
from warling_specific_ops import *
from wboperations import opcodes
import machine

scripts = [
    ('main',
     [
    (store_add, ":x", 5, 6),
    (output_int, ":x"),
    (try_begin),
        (eq, 5,6),
        (display_message, "ok"),
    (else_try),
        (try_for_range_backwards, ":x", 5, 0),
            (output_int, ":x"),
            (store_add, ":x", ":x", 1),
            (eq, ":x", 2),
            (try_begin),
                (output_int, ":x"),
            (else_try),
                (display_message, "shouln't show up"),
            (end_try),
        (end_try),
    (end_try),
     ]),

    ('simple',
    [
    ]),
]

code1 = [
]

code2 = [
]

main_code = code1

#script = warbling.WBScript("main", main_code)

machine = machine.WBMachine(scripts, opcodes)
machine.execute_script("main", [])

