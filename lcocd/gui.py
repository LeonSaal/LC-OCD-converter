# -*- coding: utf-8 -*-
"""
Created on Mon May  2 10:16:15 2022

@author: Leon
"""
import PySimpleGUI as sg

from ._funcs import (
    check_input,
    run,
    get_dirtree,
    get_files,
    draw_plot,
    clean_figure,
    get_int_bounds_from_file,
    save_to_excel,
)

from .layout import layout
import os
import copy
from .lang import lang

# Default integration bounds
default_int = [
    [30, 45, "Biopolymers"],
    [45, 59, "Humic substances"],
    [59, 66, "Low-molecular-weight acids"],
    [66, 120, "Low-molecular-weight neutrals"],
]


def gui():
    window = sg.Window(lang.prog_name, layout)
    clicked_row = None

    while True:
        event, values = window.read()

        # Close window
        if event in [sg.WIN_CLOSED]:
            break

        # Menu
        if event == "about":
            sg.popup(lang.contact_info)

        # Converter
        ## Input
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

        ## Output
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

        ## Integration
        ### Enable integration
        if event == "-C_INT-":
            if not values["-C_INT-"]:
                window["-INTEGRALS-"].update([])
            integration = [
                "-INP_0-",
                "-INP_1-",
                "-INP_NAME-",
                "-B_TAB_ADD-",
                "-B_TAB_DEL-",
                "-B_INT_DEF-",
                "-BOUNDS_INT-",
                "-B_INT_LOAD-",
            ]
            for key in integration:
                window[key].update(disabled=not values["-C_INT-"])
            if window["-B_TAB_ADD-"].get_text() == lang.add:
                window["-B_TAB_DEL-"].update(visible=False)
            else:
                window["-B_TAB_DEL-"].update(visible=True)

        ### Add row to integration table
        if event == "-B_TAB_ADD-":
            data = window["-INTEGRALS-"].get()
            selected_rows = values["-INTEGRALS-"]
            start, end, name = (
                values["-INP_0-"],
                values["-INP_1-"],
                values["-INP_NAME-"],
            )
            if check_input(start, end):
                if selected_rows and clicked_row is not None:
                    data = [
                        row if i not in selected_rows else [start, end, name]
                        for i, row in enumerate(data)
                    ]
                    window["-INTEGRALS-"].update(values=data, select_rows=[clicked_row])
                else:
                    data.append([start, end, name])
                    window["-INTEGRALS-"].update(values=data)

            else:
                window["-INP_0-"].update(0)
                window["-INP_1-"].update(120)
                sg.Popup(lang.input_warning, keep_on_top=True)

        ### Select row from integration table
        if event[0] == "-INTEGRALS-":
            clicked_row = event[2][0]
            if clicked_row is not None and clicked_row >= 0:
                data = window["-INTEGRALS-"].get()[clicked_row]
                window["-B_TAB_ADD-"].update(lang.mod)
                window["-INP_0-"].update(data[0])
                window["-INP_1-"].update(data[1])
                window["-INP_NAME-"].update(data[2])
                window["-B_TAB_DEL-"].update(visible=True)
            else:
                window["-B_TAB_ADD-"].update(lang.add)
                window["-B_TAB_DEL-"].update(visible=False)

        ### Delete selected row
        if event == "-B_TAB_DEL-":
            selected_rows = values["-INTEGRALS-"]
            if selected_rows:
                data = [
                    row
                    for i, row in enumerate(window["-INTEGRALS-"].get())
                    if i not in selected_rows
                ]
                window["-INTEGRALS-"].update(values=data)
                window["-B_TAB_ADD-"].update(lang.add)
                window["-B_TAB_DEL-"].update(visible=False)
                clicked_row = None

        ### Load default bounds
        if event == "-B_INT_DEF-":
            data = copy.deepcopy(default_int)
            window["-INTEGRALS-"].update(values=data)

        ### Load bounds from file
        if event == "-B_INT_LOAD-":
            fpath = sg.popup_get_file(
                "", no_window=True, file_types=(("Excel files", "*.xls*"),)
            )
            if fpath:
                data = get_int_bounds_from_file(fpath)
                if data:
                    window["-INTEGRALS-"].update(values=data)
                else:
                    sg.popup(lang.err_int_load, title=lang.warn)
                    os.startfile(fpath)

        ## Run conversion
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
                    save_to_excel(out, output_folder, fname)

        # Preview
        ## Select preview folder
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

        ## Select file from file table and add it to figure
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

        ## Select file from file tree
        if event == "-F_TREE-" and values["-F_TREE-"]:
            window["-T_FILES-"].update(
                get_files(window["-INP_FOLDER-"].DisplayText, values["-F_TREE-"][0])
            )

        ## Clear figure
        if event == "-FIG_CLEAR-":
            clean_figure(window)

