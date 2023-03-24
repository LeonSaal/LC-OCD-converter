import PySimpleGUI as sg
from .lang import lang
from .tabs import tab_conversion, tab_int, tab_preview, tab_settings
default_folder = ""


# Input frame
inp_frame = [
    [
        sg.Button(lang.sel_folder, key="-B_INP_FOLDER-"),
        sg.Text(default_folder, key="-INP_FOLDER-"),
    ],
    
]

# Output frame
out_frame = [
    [
        sg.Combo(
            [lang.same_folder, lang.diff_folder],
            default_value=lang.same_folder,
            key="-C_OUT_FOLDER-",
            enable_events=True,readonly=True
        )
    ],
    [
        sg.Button(lang.sel_folder, key="-B_OUT_FOLDER-"),
        sg.T(default_folder, key="-OUT_FOLDER-"),
    ],
    
]


## Complete layout
layout = [
    [
    [sg.Frame(lang.sel_conv, inp_frame, expand_x=True, expand_y=True),
     sg.Frame(lang.sel_dest, out_frame, expand_x=True, expand_y=True)],
    [sg.VPush()]],
    [
        sg.TabGroup(
            [[sg.Tab(lang.convert, tab_conversion), sg.Tab(lang.int, tab_int), sg.Tab(lang.file_prev, tab_preview), sg.Tab(lang.settings, tab_settings)]]
        ,expand_x=True)
    ]
]
