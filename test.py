__author__ = 'Lai Tash (lai.tash@yandex.ru)'
from header_operations import *
from warling_specific_ops import *
import machine

scripts = [
    ('main',
     [
         (store_add, ':x', 1, 2),
         (try_begin),
            (call_script, "script_foo"),
            (display_message, "shouldn't show up"),
         (end_try),
         (display_message, "should show up"),
     ]
    ),
    ('foo',
     [
         (display_message, "executing \"foo\""),
         (call_script, "script_bar", 5),
         (display_message, 'ororo'),
     ]
    ),

    ('bar',
     [
         (store_script_param, ":value", 1),
         (display_message, "value pushed to bar is"),
         (output_int, ":value"),
         (eq, ':value', 3),
     ]
    ),

    ('old1',
     [
         (this_or_next|eq, 5, 6),
         (this_or_next|eq, 12,8),
         (neg|this_or_next|eq, 3, 2),
         (display_message, "shouldn't show up"),
         (display_message, "should show up"),
     ]
    ),

    ('old',
     [
    (store_add, ":x", 5, 6),
    (output_int, ":x"),
    (try_begin),
        (neg|eq, 5,6),
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

