import os
import re
from itertools import chain
from typing import Mapping

import matplotlib.pyplot as plt
import PySimpleGUI as sg
from matplotlib.lines import Line2D

from .cfg import signals
from .lang import EN as lang


def draw_plot(
    window: sg.Window, values: Mapping, num: str, path: str, corr: bool, offs: Mapping
):
    from ._funcs import convert, draw_figure_w_toolbar

    # https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib_Embedded_Toolbar.py
    # ------------------------------- PASTE YOUR MATPLOTLIB CODE HERE

    fnames = [
        file
        for file in os.listdir(path)
        if file.endswith(f"{num}.dat")
        and (
            ((re.match("oc", file, flags=re.I) is not None))
            or (re.match("uv_", file, flags=re.I) is not None)
            or (re.match("uv2", file, flags=re.I) is not None)
            or (re.match("t_", file, flags=re.I) is not None)
        )
    ]
    df = convert(fnames, path, offs, corr=corr)

    lss = {"OC": "solid", "UV": "dashdot", "UV2": "dashed", "t": "dotted"}
    with plt.ion():
        plt.figure(2)
        fig = plt.gcf()
        # try:
        fig.clear(keep_observers=True)
        # except:
        #     pass
        DPI = fig.get_dpi()
        # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
        fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))
        # -------------------------------

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

        # ------------------------------- Instead of plt.show()
        # draw_figure_w_toolbar(
        #     window["-FIGURE-"].TKCanvas, fig, window["-CONTROLS-"].TKCanvas
        # )


def align_window(path: str, corr: bool, offs: Mapping):
    from ._funcs import get_files, sort_table

    values = get_files(path)
    slider = [
        [
            sg.T(f'{signal}:'),
            sg.Slider(
                (-5, 5),
                default_value=offs[signal],
                resolution=0.1,
                k=signal,
                enable_events=True,
                orientation="h",
                size=(5, 10),
            ),
        ]
        for signal in signals
    ]

    lo_ft = [
        #[sg.T(f"{lang.same_folder}: {path}")],
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
        list(chain(*slider)),
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
        ]
        + [sg.Push(), sg.B(lang.reset, k="-RESET-"), sg.OK(k="-K-")],
    ]

    frame_slider = sg.Frame(lang.offs, layout=lo_fs, expand_x=True, tooltip=lang.tip_ali_offs)

    layout = [
        [frame_table],
        [frame_slider],
        [
            sg.Push(),
            sg.Canvas(key="-CONTROLS-"),
        ],
        #     [
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

    window = sg.Window(lang.align, layout=layout)
    reverse = False
    while True:
        event, values = window.read()

        if event in [sg.WIN_CLOSED, None]:
            break

        new_offs = {signal: values[signal] for signal in signals}

        if event == "-RESET-":
            for signal in signals:
                window[signal].update(value=0)

        elif event == "-K-":
            window.close()
            return new_offs

        if type(event) == tuple:
            if event[0] == "-T_FILES-":
                row, col = event[2]
                if row == -1:
                    data = window["-T_FILES-"].get()
                    window["-T_FILES-"].update(
                        values=sort_table(data, col, reverse=reverse)
                    )
                    reverse = ~reverse

        if values["-T_FILES-"] and values["-T_FILES-"][0] >= 0:
            num = window["-T_FILES-"].get()[values["-T_FILES-"][0]][0]
            draw_plot(
                window=window,
                values=values,
                num=num,
                corr=corr,
                path=path,
                offs=new_offs,
            )

    window.close()
    return offs
