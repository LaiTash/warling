__author__ = 'Lai Tash (lai.tash@yandex.ru)'
from header_operations import *
from warling_specific_ops import *
from wboperations import opcodes
import warbling

code1 = [
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
]

code2 = [
]

main_code = code1

script = warbling.WBScript("main", main_code)

machine = warbling.WBMachine({"main": script}, opcodes)
machine.execute("main", [])

