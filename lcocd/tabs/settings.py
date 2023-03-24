import PySimpleGUI as sg
from ..lang import lang
from ..cfg import signals


## Settings tab

format_frame=[[sg.Combo(['.xlsx','.xls','.ods','.csv'], default_value='.xlsx', k='-FEXT-', readonly=True)]]

signal_frame= [[
        sg.T(lang.incl_signal),
        *[sg.CBox(signal, default=True, key=f'-{signal.upper()}-', enable_events=True) for signal in signals],
    ],
    [sg.B(lang.align, k='-ALIGN-', disabled=True, enable_events=True), sg.T('',k='-XOFFS-')]]

# Settings frame
corrections_frame = [
    # [
    #     sg.T(lang.incl_signal),
    #     *[sg.CBox(signal, default=True, key=f'-{signal.upper()}-', enable_events=True) for signal in signals],
    # ],
    [
        #sg.T(lang.corr),
        sg.CBox(lang.lin_corr, default=True, key="-CORR-"),
        
    ],
    [sg.CBox(lang.sat, default=True, key='-SATUR-')]
    #[sg.B(lang.align, k='-ALIGN-', disabled=True, enable_events=True), sg.T('',k='-XOFFS-')]
    
]


tab_settings = [
    [sg.Frame(lang.fmt, format_frame, expand_x=True)],
    [sg.Frame(lang.signal, signal_frame, expand_x=True)],
    [sg.Frame(lang.corr, corrections_frame, expand_x=True)]
    ]