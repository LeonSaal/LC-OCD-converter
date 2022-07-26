import PySimpleGUI as sg

from .cfg import signals
from .lang import lang

default_folder = ""
width = 50


# Menu
menu_definition = [[lang.info, lang.about]]

# Input frame
inp_frame = [
    [
        sg.Button(lang.sel_folder, key="-B_INP_FOLDER-"),
        sg.Text(default_folder, key="-INP_FOLDER-"),
    ],
    [sg.CBox(lang.incl_sub, default=False, key="-INP_SUBFOLDERS-")],
    [sg.CBox(lang.skip, default=True, key="-OUT_SKIP-")],
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
    [sg.CBox(lang.keep_sub, default=False, key="-OUT_SUBDIR-")],[sg.T(lang.fmt),sg.Combo(['.xlsx','.xls','.ods'], default_value='.xlsx', k='-FEXT-', readonly=True)],
]

# Settings frame
set_frame = [
    [
        sg.T(lang.incl_signal),
        *[sg.CBox(signal, default=True, key=f'-{signal.upper()}-', enable_events=True) for signal in signals],
    ],
    [
        sg.T(lang.corr),
        sg.CBox(lang.lin_corr, default=True, key="-CORR-"),
    ],
    [sg.B(lang.align, k='-ALIGN-', disabled=True, enable_events=True), sg.T('',k='-XOFFS-')]
    
]

# Integration frame
int_frame = [
    [
        sg.T(lang.int),
        sg.CBox("", key="-C_INT-", enable_events=True),
        sg.Push(),
        sg.B(
            lang.default_int,
            k="-B_INT_DEF-",
            disabled=True,
        ),
        sg.B(lang.load_int, k="-B_INT_LOAD-", disabled=True),
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
        sg.Input(0, size=[5, 1], key="-INP_0-", disabled=True),
        sg.T("-", key="-T_INT-"),
        sg.Input(120, size=[5, 1], key="-INP_1-", disabled=True),
        sg.Input("name", size=[10, 1], key="-INP_NAME-", disabled=True),
        sg.Button(lang.add, key="-B_TAB_ADD-", disabled=True),
        sg.Button(lang.delete, key="-B_TAB_DEL-", visible=False),
    ],
]

# Conversion tab
tab1_layout = [
    [sg.MenuBar(menu_definition, key="-MENU-")],
    [sg.Frame(lang.sel_conv, inp_frame, expand_x=True)],
    [sg.VPush()],
    [sg.Frame(lang.sel_dest, out_frame, expand_x=True)],
    [sg.VPush()],
    [sg.Frame(lang.settings, set_frame, expand_x=True)],
    [sg.VPush()],
    [sg.Frame(lang.int, int_frame, expand_x=True)],
    [sg.VPush()],
    [sg.Button(lang.convert, key="-RUN-", disabled=True), sg.Push()],
]

# File browser frame
folder_frame = [
    [sg.B(lang.sel_folder, key="-B_PREV_FOLDER-"), sg.T("", key="-PREV_FOLDER-")],
    [
        sg.Tree(
            sg.TreeData(),
            [],
            key="-F_TREE-",
            enable_events=True,
            expand_x=True,
            num_rows=7,
            tooltip=lang.tip_ftree,
        ),
        sg.Table(
            [[]],
            headings=[lang.file, lang.time, "OC", "UV", "UV2", "t"],
            key="-T_FILES-",
            expand_x=True,
            enable_click_events=True,
            tooltip=lang.tip_ftable,
            num_rows=7,
        ),
    ],
]

# Figure frame
figure_frame = [
    [
        sg.T(lang.incl_signal),
        sg.CBox("OC", default=True, key="-OC_P-"),
        sg.CBox("UV", default=True, key="-UV_P-"),
        sg.CBox("UV2", default=True, key="-UV2_P-"),
        sg.CBox("t", default=False, key="-T_P-"),
        sg.CBox(lang.bounds_int, default=False, k="-BOUNDS_INT-", disabled=True),
        sg.Push(),
        sg.Canvas(key="-CONTROLS-"),
        sg.B(lang.cl, key="-FIG_CLEAR-", visible=False),
    ],
    [
        sg.Column(
            layout=[
                [
                    sg.Canvas(
                        key="-FIGURE-",
                        # it's important that you set this size
                        size=(400 * 2, 400),
                    )
                ]
            ],
            background_color="#DAE0E6",
            pad=(0, 0),
        )
    ],
]

# Preview tab
tab2_layout = [
    [sg.Frame(lang.folder_browser, folder_frame, expand_x=True)],
    [sg.Frame(lang.fig, figure_frame, expand_x=True)],
]

# Complete layout
layout = [
    [
        sg.TabGroup(
            [[sg.Tab(lang.convert, tab1_layout), sg.Tab(lang.file_prev, tab2_layout)]]
        )
    ]
]
