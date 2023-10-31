import os
import re
from itertools import chain
from typing import Mapping

import matplotlib.pyplot as plt
import PySimpleGUI as sg
from matplotlib.lines import Line2D

from .cfg import signals
from .lang import EN as lang
from ._funcs import clean_figure


def draw_align_plot(
    window: sg.Window, values: Mapping, num: str, path: str, corr: bool, offs: Mapping
):
    from ._funcs import convert

    # https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib_Embedded_Toolbar.py
    # ------------------------------- PASTE YOUR MATPLOTLIB CODE HERE

    prefixes = ['OC_', 'uv_', 'uv2', 't_']
    files = os.listdir(path)
    fnames = [f'{prefix}{num}.dat' for prefix in prefixes if f'{prefix}{num}.dat' in files]
    df = convert(fnames, path, offs, corr=corr)

    lss = {"OC": "solid", "UV": "dashdot", "UV2": "dashed", "t": "dotted"}
    with plt.ion():
        plt.figure(2)
        fig = plt.gcf()
        fig.clear(keep_observers=True)

        for plot in df:
            plt.plot(df[plot], color="black", ls=lss[plot])

        plt.vlines([values["x"]], *plt.ylim(), color="gray")
        base_legend_elements = {
            "handles": [
                Line2D([0], [0], color="black", ls=ls, markersize=10)
                for ls in lss.values()
            ],
            "labels": [name for name in lss.keys()],
        }

        plt.xlabel(lang.min)
        plt.legend(**base_legend_elements, loc="upper left")
        plt.show(block=False)


def align_window(window: sg.Window, values: list, offs: Mapping):
    path=window["-INP_FOLDER-"].DisplayText
    corr=values["-CORR-"]
    num_0, num_1 = values["-FILE_SEL_COMBO_0-"], values["-FILE_SEL_COMBO_1-"]

    from ._funcs import get_files, sort_table

    values = get_files(path, num_0, num_1)
    slider = [
        [
            # sg.T(f"{signal}:"),
            sg.Slider(
                (-5, 5),
                default_value=offs[signal],
                resolution=0.1,
                k=signal,
                enable_events=True,
                orientation="h",
                size=(15, 10),
            ),
        ]
        for signal in signals
    ]
    names = [
        [
            sg.T(f"{signal}:"),
        ]
        for signal in signals
    ]

    lo_ft = [
        [
            sg.Table(
                values,
                headings=[lang.file, lang.time, *signals],
                key="-T_FILES-",
                expand_x=True,
                enable_click_events=True,
                enable_events=True,
                tooltip=lang.tip_align,
                num_rows=5,
            )
        ],
    ]
    frame_table = sg.Frame(lang.sel_file, layout=lo_ft, expand_x=True)

    lo_fs = [
        [
            sg.Column(names[:2]),
            sg.Column(slider[:2]),
            sg.Push(),
            sg.Column(names[2:]),
            sg.Column(slider[2:]),
        ],
        [
            sg.T(lang.curs),
            sg.Slider(
                (0, 120),
                default_value=60,
                resolution=0.1,
                k="x",
                orientation="h",
                enable_events=True,
                size=(20, 10),
            ),
            sg.Push(),
        ],
    ]
    frame_slider = sg.Frame(
        f"{lang.offs} ({lang.min})",
        layout=lo_fs,
        expand_x=True,
        tooltip=lang.tip_ali_offs,
    )

    layout = [
        [frame_table],
        [frame_slider],
        [sg.Push(), sg.B(lang.reset, k="-RESET-"), sg.OK(k="-K-"), sg.Push()],
    ]

    window = sg.Window(lang.align, layout=layout)
    reverse = False
    while True:
        event, values = window.read()

        if event in [sg.WIN_CLOSED, None]:
            break

        if event == "-RESET-":
            for signal in signals:
                window[signal].update(value=0)
            window["x"].update(value=60)
            clean_figure(2)

        if type(event) == tuple:
            if event[0] == "-T_FILES-":
                row, col = event[2]
                if row == -1:
                    data = window["-T_FILES-"].get()
                    window["-T_FILES-"].update(
                        values=sort_table(data, col, reverse=reverse)
                    )
                    reverse = ~reverse

        new_offs = {signal: values[signal] for signal in signals}

        if (values["-T_FILES-"] and values["-T_FILES-"][0] >= 0):
            num = window["-T_FILES-"].get()[values["-T_FILES-"][0]][0]
            draw_align_plot(
                window=window,
                values=values,
                num=num,
                corr=corr,
                path=path,
                offs=new_offs,
            )
        
            
        if event == "-K-":
            window.close()
            return new_offs
    window.close()
    return offs
