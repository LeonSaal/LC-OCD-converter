import PySimpleGUI as sg
from ..lang import lang
width = 50

# Integration frame
int_frame = [
    [
        #sg.T(lang.int),
        # sg.CBox("", key="-C_INT-", enable_events=True),
        # sg.Push(),
        
        sg.B(
            lang.default_int,
            k="-B_INT_DEF-",
        ),
        sg.B(lang.load_int, k="-B_INT_LOAD-"),sg.Push(),sg.B(lang.cl, k='-B_INT_CLEAR-')
    ],
    [
        sg.Table(
            [],
            headings=[lang.start, lang.end, lang.name],
            key="-INTEGRALS-",
            num_rows=6,
            justification="left",
            col_widths=[5, 5, width - 5],
            select_mode="extended",
            # enable_events=True,
            enable_click_events=True,
            expand_x=True,
            tooltip=lang.tip_itable,
        )
    ],
    [
        sg.Input(0, size=[5, 1], key="-INP_0-"),
        sg.T("-", key="-T_INT-"),
        sg.Input(120, size=[5, 1], key="-INP_1-"),
        sg.Input("name", size=[10, 1], key="-INP_NAME-"),
        sg.Button(lang.add, key="-B_TAB_ADD-"),
        sg.Button(lang.delete, key="-B_TAB_DEL-", visible=False),
    ],
]

## Integration Tab
tab_int = [[sg.Frame(lang.bounds_int,int_frame, expand_x=True)],[sg.T(lang.fname),sg.Input('Integrals', k='-INT_FNAME-'),sg.B(lang.int, key="-B_INT-", disabled=True)]]
