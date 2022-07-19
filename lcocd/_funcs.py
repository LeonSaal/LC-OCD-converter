# -*- coding: utf-8 -*-
"""
Created on Mon May  2 14:07:41 2022

@author: Leon
"""
import os
import re
import time
from itertools import cycle
from pathlib import Path
from typing import Iterable

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import PySimpleGUI as sg
from matplotlib import rcParams
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.lines import Line2D

from .lang import lang

colors = cycle([color["color"] for color in rcParams["axes.prop_cycle"]])
legend_elements = {"handles": [], "labels": []}
names = {"OC_": "OC", "UV_": "UV", "UV2": "UV2", "T_": "t"}

in_graph = set()

"""
    Embedding the Matplotlib toolbar into your application
"""

# ------------------------------- This is to include a matplotlib figure in a Tkinter canvas


def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side="right", fill="both", expand=1)


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


def check_input(a, b):
    if is_pos_float(a) and is_pos_float(b):
        return float(a) < float(b)
    else:
        return False


def is_pos_float(x: str):
    rep = x.replace(".", "", 1)
    if rep.isdecimal():
        if float(rep) >= 0:
            return True
    return False


def save_to_excel(out: pd.DataFrame, output_folder: str, fname: str, ext: str):
    save = False
    while not save:
        path = os.path.join(output_folder, f"{fname}{ext}")
        try:
            out.to_excel(path, merge_cells=False)
            save = True
        except PermissionError:
            fname = sg.popup_get_text(
                f'"{fname}{ext}" {lang.fopen_warning}',
                default_text=fname,
                keep_on_top=True,
            )
            if not fname:
                return


def convert(fnames, input_folder, corr=True):
    data = [
        pd.read_csv(
            os.path.join(input_folder, fname),
            sep="\s+",
            decimal=".",
            thousands=",",
            index_col=0,
            names=[names[fname[:-9].upper()]],
            engine="python",
            skiprows=1,
            encoding="latin-1",
        )
        for fname in fnames
    ]
    df = pd.concat(data, axis=1)
    if corr:
        df = df.apply(lambda x: x.subtract(min(x)))

    return df


def integrate(df, bounds):
    integrals = []
    for start, end, key in bounds:
        subset = df[(df.index >= float(start)) & (df.index < float(end))]
        integrals.append(subset.sum().rename(key))
    return pd.concat(integrals, axis=1)


def run(window, values, save=True):
    input_folder = window["-INP_FOLDER-"].DisplayText
    output_folder = window["-OUT_FOLDER-"].DisplayText
    bounds = window["-INTEGRALS-"].get()
    OC, UV, UV2, t = values["-OC-"], values["-UV-"], values["-UV2-"], values["-T-"]
    out = pd.DataFrame()
    for root, _, files in os.walk(input_folder):
        if values["-OUT_SUBDIR-"]:
            subfolder = os.path.relpath(root, input_folder)
            out_path = os.path.join(output_folder, subfolder)
            if not os.path.exists(out_path):
                os.mkdir(out_path)
        else:
            out_path = output_folder
        out_files = os.listdir(output_folder)
        nums = set(
            [
                int(file[-9:-4])
                for file in files
                if re.fullmatch(".{2,3}\d{5}\.dat", file)
            ]
        )

        for i, num in enumerate(nums):
            f_out = f"{num}{values['-FEXT-']}"
            if f_out in out_files:
                if values["-OUT_SKIP-"]:
                    msg = f'"{f_out}" {lang.fout_exist}'
                else:
                    msg = f'{lang.overwr} "{f_out}"'
            else:
                msg = f'{lang.curr_sample} "{num}"'

            if not sg.one_line_progress_meter(
                lang.convo,
                i + 1,
                len(nums),
                root,
                msg,
                orientation="h",
            ):
                return out

            if f_out in out_files and values["-OUT_SKIP-"]:
                continue
            fnames = [
                file
                for file in files
                if file.endswith(f"{num}.dat")
                and (
                    ((re.match("oc", file, flags=re.I) is not None) & OC)
                    or ((re.match("uv_", file, flags=re.I) is not None) & UV)
                    or ((re.match("uv2", file, flags=re.I) is not None) & UV2)
                    or ((re.match("t_", file, flags=re.I) is not None) & t)
                )
            ]
            if fnames:
                df = convert(fnames, root, corr=values["-CORR-"])

                if save:
                    save_to_excel(df, output_folder, f"{num}", values["-FEXT-"])

                if window["-INTEGRALS-"].get() != []:
                    integrals = pd.concat(
                        [integrate(df, bounds)],
                        keys=[(num)],
                        names=[lang.sample, lang.signal],
                    )
                    out = pd.concat([out, integrals], axis=0)
        if not values["-INP_SUBFOLDERS-"]:
            if not nums:
                sg.popup(f'{lang.no_file_warning} in "{root}"')
            break
    return out


def get_dirtree(grandparent):
    treedata = sg.TreeData()
    grandparent = Path(grandparent)
    treedata.insert("", grandparent.as_posix(), grandparent.name, [])
    for root, _, _ in os.walk(grandparent):
        parent = Path(root).parent.as_posix()
        child = Path(root)
        name = child.name
        if child != grandparent:
            treedata.insert(parent, child.as_posix(), name, [])
    return treedata


def get_files(parent, path):
    prefix = ["OC_", "UV_", "UV2", "T_"]
    files = os.listdir(path)
    nums = list(
        set([file[-9:-4] for file in files if re.fullmatch(".{2,3}\d{5}\.dat", file)])
    )
    signals = {
        num: {
            "files": [file[:-9].upper() for file in files if num in file],
            "time": min(
                [
                    os.path.getctime(os.path.join(path, file))
                    for file in files
                    if num in file
                ]
            ),
        }
        for num in nums
    }
    return [
        [
            num,
            time.strftime("%Y-%m-%d", time.localtime(dat["time"])),
            *["x" if p in dat["files"] else "" for p in prefix],
        ]
        for num, dat in signals.items()
    ]


def sort_table(values: Iterable, col: int, reverse: bool):
    return sorted(values, key=lambda x: x[col], reverse=reverse)


def draw_plot(window, values, num):
    # https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib_Embedded_Toolbar.py
    # ------------------------------- PASTE YOUR MATPLOTLIB CODE HERE
    path = values["-F_TREE-"][0]
    OC, UV, UV2, t = (
        values["-OC_P-"],
        values["-UV_P-"],
        values["-UV2_P-"],
        values["-T_P-"],
    )
    fnames = [
        file
        for file in os.listdir(path)
        if file.endswith(f"{num}.dat")
        and (
            ((re.match("oc", file, flags=re.I) is not None) & OC)
            or ((re.match("uv_", file, flags=re.I) is not None) & UV)
            or ((re.match("uv2", file, flags=re.I) is not None) & UV2)
            or ((re.match("t_", file, flags=re.I) is not None) & t)
        )
    ]
    if fnames:
        df = convert(fnames, path, corr=values["-CORR-"])

    else:
        return

    lss = {"OC": "solid", "UV": "dashdot", "UV2": "dashed", "t": "dotted"}
    plt.figure(1)
    fig = plt.gcf()
    DPI = fig.get_dpi()
    # ------------------------------- you have to play with this size to reduce the movement error when the mouse hovers over the figure, it's close to canvas size
    fig.set_size_inches(404 * 2 / float(DPI), 404 / float(DPI))
    # -------------------------------
    to_add = [col for col in df.columns if num not in legend_elements["labels"]]
    if not to_add:
        return
    in_graph.update(to_add)
    color = next(colors)

    for plot in to_add:
        plt.plot(df[plot], color=color, ls=lss[plot])

    if values["-BOUNDS_INT-"]:
        start = [elem[0] for elem in window["-INTEGRALS-"].get()]
        plt.vlines(start, ymin=0, ymax=plt.ylim()[1], colors="gray")

    legend_elements["handles"].append(
        Line2D(
            [0],
            [0],
            marker="o",
            markerfacecolor=color,
            markeredgecolor="none",
            ls="none",
            markersize=10,
        )
    )
    legend_elements["labels"].append(f"{num}")
    print(to_add, in_graph, lss)
    base_legend_elements = {
        "handles": [
            Line2D([0], [0], color="black", ls=ls, markersize=10)
            for key, ls in lss.items()
            if key in in_graph
        ],
        "labels": [name for key, name in names.items() if name in in_graph],
    }

    objs = plt.gca().findobj(matplotlib.legend.Legend)
    for obj in objs:
        obj.remove()

    plt.xlabel(lang.min)
    base_legend = plt.legend(**base_legend_elements, loc="upper left")
    plt.legend(**legend_elements, loc="upper right")
    plt.gca().add_artist(base_legend)

    # ------------------------------- Instead of plt.show()
    draw_figure_w_toolbar(
        window["-FIGURE-"].TKCanvas, fig, window["-CONTROLS-"].TKCanvas
    )


def clean_figure(window):
    global legend_elements, colors, in_graph
    in_graph = set()
    colors = cycle([color["color"] for color in rcParams["axes.prop_cycle"]])
    legend_elements = {"handles": [], "labels": []}
    fig = plt.gcf()
    fig.clear(keep_observers=True)
    draw_figure_w_toolbar(
        window["-FIGURE-"].TKCanvas, fig, window["-CONTROLS-"].TKCanvas
    )
    window["-FIG_CLEAR-"].update(disabled=True)


def get_int_bounds_from_file(path):
    header = ["start", "end", "name"]
    df = pd.read_excel(path, header=0)
    for name in header:
        if name not in df.columns:
            return None
        if name != "name":
            df[[name]] = df[[name]].applymap(lambda x: to_float(x))
            df.dropna(inplace=True)
    return df[header].values.tolist()


def to_float(x):
    out = pd.to_numeric(x, errors="coerce")
    if pd.isna(out):
        return pd.NA
    else:
        return out
