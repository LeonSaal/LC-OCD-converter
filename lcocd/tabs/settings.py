import PySimpleGUI as sg
from ..lang import lang
from ..cfg import signals


## Settings tab

format_frame = [
    [
        sg.Combo(
            [".xlsx", ".xls", ".ods", ".csv"],
            default_value=".csv",
            k="-FEXT-",
            readonly=True,
            enable_events=True,
        )
    ]
]

browse_frame = [
    [sg.T(lang.files_per_page),sg.Combo([25, 50, 100, 250, 500], default_value=100, k="-MAX_DIR-", readonly=True, enable_events=True)]
]

signal_frame = [
    [
        sg.T(lang.incl_signal),
        *[
            sg.CBox(signal, default=True, key=f"-{signal.upper()}-", enable_events=True)
            for signal in signals
        ],
    ],
    [
        sg.B(lang.align, k="-ALIGN-", disabled=True, enable_events=True),
        sg.T("", k="-XOFFS-"),
    ],
]

# Settings frame
corrections_frame = [
    [
        # sg.T(lang.corr),
        sg.CBox(lang.lin_corr, default=True, key="-CORR-"),
    ],
    [sg.CBox(lang.sat, default=True, key="-SATUR-")],
]


tab_settings = [
    [sg.Frame(lang.fmt, format_frame, expand_x=True), sg.Frame(lang.browse_files, browse_frame, expand_x=True)],
    [sg.Frame(lang.signal, signal_frame, expand_x=True)],
    [sg.Frame(lang.corr, corrections_frame, expand_x=True)],
    [sg.Push(), sg.B(lang.reset, key="-RESET_SETTINGS-", tooltip=lang.tip_reset)],
]
