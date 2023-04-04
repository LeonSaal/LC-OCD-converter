# -*- coding: utf-8 -*-
"""
Created on Mon May  2 10:16:15 2022

@author: Leon
"""
import configparser
import copy
import os
import webbrowser

import PySimpleGUI as sg

from ._align import align_window
from ._funcs import (
    check_input,
    clean_figure,
    draw_plot,
    get_dirtree,
    get_files,
    get_int_bounds_from_file,
    run,
    save_data,
    sort_table,
)
from .cfg import SET_FILE, INT_FILE, default_int, signals
from .lang import lang
from .layout import layout
from .tabs.integrate import headings
import pandas as pd


# Default integration bounds


def info_window() -> None:
    links = {
        "-MAIL-": [lang.contact, lang.mail],
        "-WEB-": [lang.proj, lang.project_link],
        "-DOI-": [lang.defa_int_bounds, lang.int_bounds_link],
    }
    layout = [
        [sg.T("Leon Saal, 2023")],
        [sg.B(vals[0], k=key, tooltip=vals[1]) for key, vals in links.items()],
    ]
    window = sg.Window(lang.info, layout=layout)

    while True:
        event, _ = window.read()
        if event == sg.WIN_CLOSED:
            break
        if event == "-MAIL-":
            webbrowser.open(f"mailto:{lang.mail}", new=1)
        elif event == "-WEB-":
            webbrowser.open(lang.project_link)
        elif event == "-DOI-":
            webbrowser.open(lang.int_bounds_link)
    window.close()


def update_int(window: sg.Window, integrate: bool):
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
        window[key].update(disabled=not integrate)
    pass


def update_window(window):
    if window["-INP_FOLDER-"].DisplayText and window["-OUT_FOLDER-"].DisplayText:
        window["-RUN-"].update(disabled=False)
        window["-B_INT-"].update(disabled=False)
    else:
        window["-RUN-"].update(disabled=True)
        window["-B_INT-"].update(disabled=True)


def gui() -> None:
    window = sg.Window(
        lang.prog_name, layout, finalize=True, enable_close_attempted_event=True
    )
    clicked_row = None
    reverse = False
    SAVE_SETTINGS = True

    offs = {signal: 0 for signal in signals}
    cfg = configparser.ConfigParser()

    if os.path.exists(SET_FILE):
        cfg.read(SET_FILE)
        if "values" in cfg:
            for key, value in cfg["values"].items():
                if key.upper() in window.key_dict:
                    if value in ["True", "False"]:
                        val = eval(value)
                    else:
                        val = str(value)
                    window[key.upper()].update(val)

        if "offset" in cfg:
            for signal in signals:
                if signal.lower() in cfg["offset"]:
                    num = cfg["offset"][signal.lower()]
                    try:
                        offs[signal] = float(num)
                    except:
                        pass
            text = f'{", ".join([f"{sig}: {off} {lang.min}" for sig, off in offs.items() if off!=0])}'
            if text:
                window["-XOFFS-"].update(f"{lang.offs}: " + text)
        update_window(window)
        if window["-INP_FOLDER-"].DisplayText:
            text = window["-INP_FOLDER-"].DisplayText
            window["-F_TREE-"].update(get_dirtree(text))
            window["-ALIGN-"].update(disabled=False)

    if os.path.exists(INT_FILE):
        data = get_int_bounds_from_file(INT_FILE)
        window["-INTEGRALS-"].update(data)

    while True:
        event, values = window.read()

        # Close window
        if event in [sg.WIN_CLOSE_ATTEMPTED_EVENT]:
            if window["-INTEGRALS-"].get() != []:
                data = pd.DataFrame(window["-INTEGRALS-"].get())
                data.rename(
                    {old: new for old, new in zip(data.columns, headings)},
                    axis=1,
                    inplace=True,
                )
                data.to_csv(INT_FILE, index=False)
            else:
                if os.path.exists(INT_FILE):
                    os.remove(INT_FILE)
            if not SAVE_SETTINGS:
                break
            if "values" not in cfg:
                cfg.add_section("values")
            if "offset" not in cfg:
                cfg.add_section("offset")
            for key, val in values.items():
                if (
                    (val is not None)
                    and (type(val) != list)
                    and not str(key).isnumeric()
                ):
                    cfg["values"][key] = str(val)
            for key, val in window.key_dict.items():
                if isinstance(val, sg.T):
                    cfg["values"][key] = val.DisplayText

            for key, val in offs.items():
                cfg["offset"][key] = str(val)

            with open(SET_FILE, "w") as configfile:
                cfg.write(configfile)

            break

        # Menu
        if event == "about":
            info_window()

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
                window["-ALIGN-"].update(disabled=False)
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

        update_window(window)

        ## Settings
        if event == "-ALIGN-":
            new_offs = align_window(
                path=window["-INP_FOLDER-"].DisplayText,
                corr=values["-CORR-"],
                offs=offs,
            )
            if new_offs:
                offs = new_offs
            if sum([abs(val) for val in offs.values()]) != 0:
                text = f'{lang.offs}: {", ".join([f"{sig}: {off} {lang.min}" for sig, off in offs.items() if off!=0])}'
                window["-XOFFS-"].update(text)
            else:
                window["-XOFFS-"].update("")

        ## Integration
        ### Enable integration
        if event == "-B_INT_CLEAR-":
            window["-INTEGRALS-"].update([])

        ### Add row to integration table
        if event == "-B_TAB_ADD-":
            data = window["-INTEGRALS-"].get()
            selected_rows = values["-INTEGRALS-"]
            start, end, name = (
                values["-INP_0-"].replace(",", "."),
                values["-INP_1-"].replace(",", "."),
                values["-INP_NAME-"],
            )
            if check_input(start, end):
                if selected_rows and clicked_row is not None:
                    data = [
                        row
                        if i not in selected_rows
                        else [float(start), float(end), name]
                        for i, row in enumerate(data)
                    ]
                    window["-INTEGRALS-"].update(values=data, select_rows=[clicked_row])
                else:
                    data.append([float(start), float(end), name])
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
                "",
                no_window=True,
                file_types=(
                    ("Excel files", "*.xls*"),
                    ("CSV files", "*.csv"),
                ),
            )
            if fpath:
                data = get_int_bounds_from_file(fpath)
                if data:
                    window["-INTEGRALS-"].update(values=data)
                else:
                    sg.popup(lang.err_int_load, title=lang.warn)
                    os.startfile(fpath)

        ### Run integration
        if (event == "-B_INT-") and (window["-INTEGRALS-"].get() != []):
            output_folder = window["-OUT_FOLDER-"].DisplayText
            out = run(window, values, offs, job=lang.int)
            # mindex = pd.MultiIndex.from_tuples([(key, f'{start} - {end}') for start, end, key in window["-INTEGRALS-"].get()])
            # out.columns = mindex
            if not out.empty:
                fname = window["-INT_FNAME-"].get()
                save_data(out, output_folder, fname, values)

        ## Run conversion
        if event == "-RUN-":
            output_folder = window["-OUT_FOLDER-"].DisplayText
            out = run(window, values, offs, job=lang.convo)

        # Preview
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
                draw_plot(window, values, num, offs)
                window["-FIG_CLEAR-"].update(disabled=False, visible=True)
            elif selected_file == -1:
                data = window["-T_FILES-"].get()
                window["-T_FILES-"].update(
                    values=sort_table(data, event[2][1], reverse=reverse)
                )
                reverse = ~reverse

        ## Select file from file tree
        if event == "-F_TREE-" and values["-F_TREE-"]:
            data = get_files(values["-F_TREE-"][0])
            window["-T_FILES-"].update(sort_table(data, 0, reverse=reverse))

        ## Clear figure
        if event == "-FIG_CLEAR-":
            clean_figure(window)

        # Settings

        if event == "-RESET_SETTINGS-":
            if os.path.exists(SET_FILE):
                os.remove(SET_FILE)
            SAVE_SETTINGS = False
            sg.popup(lang.tip_reset)
