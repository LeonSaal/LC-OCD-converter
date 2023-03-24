import PySimpleGUI as sg
from ..lang import lang


## Preview tab
# File browser frame
folder_frame = [
    #[sg.B(lang.sel_folder, key="-B_PREV_FOLDER-"), sg.T("", key="-PREV_FOLDER-")],
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
        sg.CBox(lang.bounds_int, default=False, k="-BOUNDS_INT-"),#, disabled=True),
        sg.Push(),
        sg.Canvas(key="-CONTROLS-"),
        sg.B(lang.cl, key="-FIG_CLEAR-", visible=False),
    ],
    # [
    #     sg.Column(
    #         layout=[
    #             [
    #                 sg.Canvas(
    #                     key="-FIGURE-",
    #                     # it's important that you set this size
    #                     size=(400 * 2, 400),
    #                 )
    #             ]
    #         ],
    #         background_color="#DAE0E6",
    #         pad=(0, 0),
    #     )
    # ],
]

tab_preview = [
    [sg.Frame(lang.folder_browser, folder_frame, expand_x=True)],
    [sg.Frame(lang.fig, figure_frame, expand_x=True)],
]
