# -*- coding: utf-8 -*-
"""
Created on Mon May  2 10:16:15 2022

@author: Leon
"""
import PySimpleGUI as sg
from dotmap import DotMap
from ._funcs import (
    check_input,
    run,
    get_dirtree,
    get_files,
    draw_plot,
    clean_figure,
    get_int_bounds_from_file
)
import os
import copy


fonts = DotMap()
fonts.head = "Calibri 15 bold"
fonts.sub = "Calibri 10 bold"

default_folder = ""  # r'C:\Users\Leon\tubCloud2\Shared\LC-OCD\Rohdaten'
width = 50

lang = DotMap()
lang.sel_conv = "Select files to convert"
lang.sel_folder = "Select folder"
lang.incl_sub = "Include subdirectories"
lang.sel_dest = "Select destination folder"
lang.skip = "Skip if destination file already exists"
lang.same_folder = "source folder"
lang.diff_folder = "different folder"
lang.keep_sub = "Keep folder structure"
lang.settings = "Settings"
lang.incl_signal = "Include:"
lang.corr = "Corrections:"
lang.lin_corr = "Linear baseline-correction"
lang.int = "Integrate"
lang.add = "add"
lang.delete = "delete"
lang.mod = "modify"
lang.convert = "convert"
lang.exit = "exit"
lang.enter_fname = "Please enter a file name"
lang.start = "start"
lang.name = "name"
lang.end = "end"
lang.out_fname = "Destination file:"
lang.input_warning = f"{lang.start} and {lang.end} must be both positive numbers and {lang.start} < {lang.end}!"
lang.fopen_warning = "is openened by another program. Please enter new name!"
lang.prog_name = "LC-OCD converter"
lang.info = "info"
lang.about = "about"
lang.contact_info = "Leon Saal\nleon.saal@uba.de\n2022"
lang.file = "files"
lang.file_prev = "file preview"
lang.cl = "clear"
lang.tip_ftable = "click row to add to graph below"
lang.tip_itable = "click on row to modify/delete, below to add rows"
lang.tip_ftree = "click on element to list files"
lang.folder_browser = "browse folders"
lang.fig = "figure"
lang.default_int = "load default"
lang.bounds_int = "Integration bounds"
lang.load_int = "load from file"
lang.err_int_load = 'Error loading from file. File must contain "start", "end" and "name" in header.'
lang.warn = "Warning"

default_int = [[30, 45, "Biopolymers"],[45, 59, "Humic substances"],[59, 66, "Low-molecular-weight acids"],[66, 120, "Low-molecular-weight neutrals"]]

menu_definition = [[lang.info, lang.about]]

def gui():
    inp_frame = [
        [
            sg.Button(lang.sel_folder, key="-B_INP_FOLDER-"),
            sg.Text(default_folder, key="-INP_FOLDER-"),
        ],
        [sg.CBox(lang.incl_sub, default=False, key="-INP_SUBFOLDERS-")],
        [sg.CBox(lang.skip, default=True, key="-OUT_SKIP-")],
    ]
    out_frame = [
        [
            sg.Combo(
                [lang.same_folder, lang.diff_folder],
                default_value=lang.same_folder,
                key="-C_OUT_FOLDER-",
                enable_events=True,
            )
        ],
        [
            sg.Button(lang.sel_folder, key="-B_OUT_FOLDER-"),
            sg.T(default_folder, key="-OUT_FOLDER-"),
        ],
        [sg.CBox(lang.keep_sub, default=False, key="-OUT_SUBDIR-")],
    ]

    set_frame = [
        [
            sg.T(lang.incl_signal, font=fonts.sub),
            sg.CBox("OC", default=True, key="-OC-"),
            sg.CBox("UV", default=True, key="-UV-"),
            sg.CBox("UV2", default=True, key="-UV2-"),
            sg.CBox("t", default=False, key="-T-"),
        ],
        [
            sg.T(lang.corr, font=fonts.sub),
            sg.CBox(lang.lin_corr, default=True, key="-CORR-"),
        ],
    ]

    int_frame = [
        [sg.T(lang.int, font=fonts.sub), sg.CBox("", key="-C_INT-", enable_events=True) ,sg.Push(),
        sg.B(lang.default_int, k='-B_INT_DEF-', disabled=True,tooltip="doi:10.1016/j.watres.2007.05.029"),
        sg.B(lang.load_int, k='-B_INT_LOAD-', disabled=True)],
        [
            sg.Table(
                [],
                headings=[lang.start, lang.end, lang.name],
                key="-INTEGRALS-",
                num_rows=6,
                justification= 'left',
                col_widths=[5, 5, width - 5],
                select_mode="extended",
                #enable_events=True, 
                enable_click_events=True,
                expand_x=True,
                tooltip=lang.tip_itable,
            )
        ],
        [
            sg.Input(0, size=[3, 1], key="-INP_0-", disabled=True),
            sg.T("-", key="-T_INT-"),
            sg.Input(120, size=[3, 1], key="-INP_1-", disabled=True),
            sg.Input("name", size=[10, 1], key="-INP_NAME-", disabled=True),
            sg.Button(lang.add, key="-B_TAB_ADD-", disabled=True),
            sg.Button(lang.delete, key="-B_TAB_DEL-", visible=False)
        ],
    ]

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
        [sg.Button(lang.convert, key="-RUN-"), sg.Push()],
    ]

    folder_frame = [
        [sg.B(lang.sel_folder, key="-B_PREV_FOLDER-"), sg.T("", key="-PREV_FOLDER-")],
        [
            sg.Tree(
                sg.TreeData(),
                [],
                key="-F_TREE-",
                enable_events=True,
                expand_x=True,
                num_rows=5,
                tooltip=lang.tip_ftree,
            ),
            sg.Table(
                [[]],
                headings=[lang.file, "OC", "UV", "UV2", "t"],
                key="-T_FILES-",
                expand_x=True,
                enable_click_events=True,
                tooltip=lang.tip_ftable,
                num_rows=5,
            ),
        ],
    ]

    figure_frame = [
        [
            sg.T(lang.incl_signal, font=fonts.sub),
            sg.CBox("OC", default=True, key="-OC_P-"),
            sg.CBox("UV", default=True, key="-UV_P-"),
            sg.CBox("UV2", default=True, key="-UV2_P-"),
            sg.CBox("t", default=False, key="-T_P-"),
            sg.CBox(lang.bounds_int, default=False, k='-BOUNDS_INT-', disabled=True),
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


    tab2_layout = [
        [sg.Frame(lang.folder_browser, folder_frame, expand_x=True)],
        [sg.Frame(lang.fig, figure_frame, expand_x=True)],
    ]

    layout = [
        [
            sg.TabGroup(
                [[sg.Tab(lang.convert, tab1_layout), sg.Tab(lang.file_prev, tab2_layout)]]
            )
        ]
    ]

    window = sg.Window(lang.prog_name, layout)

    clicked_row = None


    while True:
        # Converter
        event, values = window.read()
        if event == "about":
            sg.popup(lang.contact_info)

        if event in [sg.WIN_CLOSED]:  # if user closes window or clicks cancel
            break

        # Input
        if event == "-B_INP_FOLDER-":
            text = sg.popup_get_folder(
                lang.enter_fname,
                no_window=True,
                initial_folder=window["-INP_FOLDER-"].DisplayText,
            )
            if text:
                window["-INP_FOLDER-"].update(text)
                if not window["-PREV_FOLDER-"].DisplayText:
                    window["-PREV_FOLDER-"].update(text)
                    window["-F_TREE-"].update(get_dirtree(text))
                if values["-C_OUT_FOLDER-"] == lang.same_folder:
                    window["-OUT_FOLDER-"].update(text)

        # Output
        if (
            event == "-C_OUT_FOLDER-"
            and values["-C_OUT_FOLDER-"] == lang.diff_folder
            or event == "-B_OUT_FOLDER-"
        ):
            text = sg.popup_get_folder(
                lang.enter_fname,
                no_window=True,
                initial_folder=window["-OUT_FOLDER-"].DisplayText,
            )
            if text:
                window["-OUT_FOLDER-"].update(text)
                window["-C_OUT_FOLDER-"].update(lang.diff_folder)

        if event == "-C_OUT_FOLDER-" and values["-C_OUT_FOLDER-"] == lang.same_folder:
            window["-OUT_FOLDER-"].update(window["-INP_FOLDER-"].DisplayText)

        # Integration
        if event == "-C_INT-":
            if not values["-C_INT-"]:
                window["-INTEGRALS-"].update([])
            integration = ["-INP_0-", "-INP_1-", "-INP_NAME-", "-B_TAB_ADD-", "-B_TAB_DEL-", "-B_INT_DEF-", "-BOUNDS_INT-", '-B_INT_LOAD-']
            for key in integration:
                window[key].update(disabled=not values["-C_INT-"])
            if window["-B_TAB_ADD-"].get_text() == lang.add:
                window["-B_TAB_DEL-"].update(visible=False)
            else:
                window["-B_TAB_DEL-"].update(visible=True)

        if event == "-B_TAB_ADD-":
            data = window["-INTEGRALS-"].get()
            selected_rows = values['-INTEGRALS-']
            start, end, name = values["-INP_0-"], values["-INP_1-"], values["-INP_NAME-"]
            if check_input(start, end):
                if selected_rows and clicked_row is not None:
                    data = [row if i not in selected_rows else [start, end, name] for i, row in enumerate(data)]
                    window["-INTEGRALS-"].update(values=data, select_rows=[clicked_row])
                else:
                    data.append([start, end, name])
                    window["-INTEGRALS-"].update(values=data)
                
            else:
                window["-INP_0-"].update(0)
                window["-INP_1-"].update(120)
                sg.Popup(lang.input_warning, keep_on_top=True)

        if event[0] == "-INTEGRALS-":
            clicked_row = event[2][0]
            if clicked_row is not None and clicked_row >=0:
                data = window["-INTEGRALS-"].get()[clicked_row]
                window["-B_TAB_ADD-"].update(lang.mod)
                window["-INP_0-"].update(data[0])
                window["-INP_1-"].update(data[1])
                window["-INP_NAME-"].update(data[2])
                window["-B_TAB_DEL-"].update(visible=True)
            else:
                window["-B_TAB_ADD-"].update(lang.add)
                window["-B_TAB_DEL-"].update(visible=False)

        if event == "-B_TAB_DEL-":
            selected_rows = values['-INTEGRALS-']
            if selected_rows:
                data = [row for i, row in enumerate(window["-INTEGRALS-"].get()) if i not in selected_rows]
                window["-INTEGRALS-"].update(values=data)
                window["-B_TAB_ADD-"].update(lang.add)
                window["-B_TAB_DEL-"].update(visible=False)
                clicked_row = None

        if event == "-B_INT_DEF-":
            data = copy.deepcopy(default_int)
            window["-INTEGRALS-"].update(values=data)

        if event == '-B_INT_LOAD-':
            fpath = sg.popup_get_file("",no_window=True, file_types=(("Excel files", "*.xls*"),))
            if fpath:
                data = get_int_bounds_from_file(fpath)
                if data:
                    window["-INTEGRALS-"].update(values=data)
                else:
                    sg.popup(lang.err_int_load, title = lang.warn)
                    os.startfile(fpath)

        # Run
        if event == "-RUN-":
            if not window["-INP_FOLDER-"].DisplayText:
                sg.popup(lang.sel_conv)
                text = sg.popup_get_folder(lang.enter_fname, no_window=True)
                if text:
                    window["-INP_FOLDER-"].update(text)
                    if values["-C_OUT_FOLDER-"] == lang.same_folder:
                        window["-OUT_FOLDER-"].update(text)
                    window["-F_TREE-"].update(get_dirtree(text))
            else:
                output_folder = window["-OUT_FOLDER-"].DisplayText
                out = run(window, values)
                if (window["-INTEGRALS-"].get() != []) and not out.empty:
                    fname = "Integrals"
                    save = False
                    while not save:
                        path = os.path.join(output_folder, f"{fname}.xlsx")
                        try:
                            out.to_excel(path, merge_cells=False)
                            sg.popup(f"{lang.out_fname} {path}", keep_on_top=True)
                            save = True
                        except PermissionError:
                            fname = sg.popup_get_text(
                                f'"{fname}.xlsx" {lang.fopen_warning}',
                                default_text=fname,
                                keep_on_top=True,
                            )
        # Preview
        if event == "-B_PREV_FOLDER-":
            text = sg.popup_get_folder(
                lang.enter_fname,
                no_window=True,
                initial_folder=window["-PREV_FOLDER-"].DisplayText,
            )
            if text:
                window["-PREV_FOLDER-"].update(text)
                window["-F_TREE-"].update(get_dirtree(text))
                window["-T_FILES-"].update([])

        if event[0] == "-T_FILES-":
            selected_file = event[2][0]
            if (
                selected_file is not None
                and selected_file >= 0
                and values["-F_TREE-"]
                and (
                    values["-UV_P-"]
                    or values["-UV2_P-"]
                    or values["-OC_P-"]
                    or values["-T_P-"]
                )
            ):
                num = window["-T_FILES-"].get()[selected_file][0]
                draw_plot(window, values, num)
                window["-FIG_CLEAR-"].update(disabled=False, visible=True)

        if event == "-F_TREE-" and values["-F_TREE-"]:
            window["-T_FILES-"].update(
                get_files(window["-INP_FOLDER-"].DisplayText, values["-F_TREE-"][0])
            )

        if event == "-FIG_CLEAR-":
            clean_figure(window)

        

