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
from typing import Iterable, Mapping

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PySimpleGUI as sg
from matplotlib import rcParams
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.lines import Line2D

from .lang import lang
from .cfg import AU_THRESH, FILE_PREFIXES

colors = cycle([color["color"] for color in rcParams["axes.prop_cycle"]])
legend_elements = {"handles": [], "labels": []}
names = {"OC_": "OC", "UV_": "UV", "UV2": "UV2", "T_": "t"}

in_graph = set()

"""
    Embedding the Matplotlib toolbar into your application
"""

# ------------------------------- This is to include a matplotlib figure in a Tkinter canvas


# def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
#     if canvas.children:
#         for child in canvas.winfo_children():
#             child.destroy()
#     if canvas_toolbar.children:
#         for child in canvas_toolbar.winfo_children():
#             child.destroy()
#     figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
#     figure_canvas_agg.draw()
#     toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
#     toolbar.update()
#     figure_canvas_agg.get_tk_widget().pack(side="right", fill="both", expand=1)


# class Toolbar(NavigationToolbar2Tk):
#     def __init__(self, *args, **kwargs):
#         super(Toolbar, self).__init__(*args, **kwargs)


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


def save_data(out: pd.DataFrame, output_folder: str, fname: str, values: dict):
    save = False
    ext = values["-FEXT-"]
    while not save:
        path = os.path.join(output_folder, f"{fname}{ext}")
        try:
            out.to_excel(path, merge_cells=False) if ext != ".csv" else out.to_csv(path)
            save = True
        except PermissionError:
            fname = sg.popup_get_text(
                f'"{fname}{ext}" {lang.fopen_warning}',
                default_text=fname,
                keep_on_top=True,
            )
            if not fname:
                return


def shift(df: pd.DataFrame, toff: float):
    ioff = df.index.get_indexer([abs(toff)], method="nearest")[0]
    sign = np.sign(toff)
    return df.shift(int(sign * ioff), fill_value=min(df.values)[0])

def get_ana_name(fname: str, input_folder: str):
    with open(os.path.join(input_folder, fname)) as f:
        return f.readline().strip()

def convert(fnames: Iterable, input_folder: str, offs: Mapping, corr: bool = True):
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
    data = [shift(df, offs[df.columns[0]]) for df in data]
    df = pd.concat(data, axis=1)
    if corr:
        df = df.apply(lambda x: x.subtract(min(x), fill_value=min(x)))
    return df


def integrate(df, bounds):
    integrals = []
    for start, end, key in bounds:
        subset = df[(df.index >= float(start)) & (df.index < float(end))]
        integrals.append(subset.sum().rename(f"{key} ({start} - {end} {lang.min})"))
    return pd.concat(integrals, axis=1)


def run(window: sg.Window, values: Mapping, offs: Mapping, job: str):
    # get parameters from UI
    input_folder = window["-INP_FOLDER-"].DisplayText
    output_folder = window["-OUT_FOLDER-"].DisplayText
    bounds = window["-INTEGRALS-"].get()
    num_0, num_1 = values["-FILE_SEL_COMBO_0-"], values["-FILE_SEL_COMBO_1-"]
    selected = values["-OC-"], values["-UV-"], values["-UV2-"], values["-T-"]

    #setup output
    out = pd.DataFrame()
    n = {"skipped": 0, "overwr": 0, "total": 0}

    # loop over input directory (optional: subdirectories)
    for root, _, files in os.walk(input_folder):
        if values["-OUT_SUBDIR-"]:
            subfolder = os.path.relpath(root, input_folder)
            out_path = os.path.join(output_folder, subfolder)
            if not os.path.exists(out_path):
                os.mkdir(out_path)
        else:
            out_path = output_folder
        
        # list files in outputfolder to check for skippable files
        out_files = os.listdir(output_folder)
        nums = sorted(list(set(
            [
                file[-9:-4]
                for file in files
                if re.fullmatch(".{2,3}\d{5}\.dat", file)
            ]
        )), reverse=True)

        # iterate over analysis numbers in input directory
        nums = [num for num in nums if (num_0 <= num <= num_1)]
        for i, num in enumerate(nums):
            skip = False
            n["total"] += 1
            
            fnames = [f'{prefix}{num}.dat' for prefix, select in zip(FILE_PREFIXES, selected) if select and f'{prefix}{num}.dat' in files]
            ananame = get_ana_name(fname=fnames[0], input_folder=root)
            f_out = f"{num}_{ananame}"

            # check wheteher to skip or overwrite output file
            if (f"{f_out}{values['-FEXT-']}" in out_files) and job == lang.convo:
                if values["-OUT_SKIP-"]:
                    msg = f'"{f_out}" {lang.fout_exist}'
                    n["skipped"] += 1
                    skip = True
                else:
                    msg = f'{lang.overwr} "{f_out}"'
                    n["overwr"] += 1
            else:
                msg = f'{lang.curr_sample} "{num}"'

            # update progress
            if not sg.one_line_progress_meter(
                job,
                i + 1,
                len(nums),
                root,
                msg,
                orientation="h",
            ):
                return out
            if skip:
                continue

            if fnames:
                df = convert(fnames, root, offs, corr=values["-CORR-"])
                
                if job == lang.convo:
                    save_data(df, output_folder, f_out, values)

                if window["-INTEGRALS-"].get() != []:
                    integrals = pd.concat(
                        [integrate(df, bounds)],
                        keys=[(num, ananame)],
                        names=[lang.sample, lang.name,lang.signal],
                    )
                    if values["-SATUR-"]:
                        warning_text = ", ".join(
                            [
                                key
                                for key, value in AU_THRESH.items()
                                if ((key in df) and (df[key].max() > value))
                            ]
                        )
                        integrals["SATURATION_WARNING"] = warning_text

                    out = pd.concat([out, integrals], axis=0)

        if not values["-INP_SUBFOLDERS-"]:
            if not nums:
                sg.popup(f'{lang.no_file_warning} in "{root}"')
            break

    summary_text = f'{lang.total}: {n["total"]}'
    if job == lang.convo:
        summary_text += (
            f'\n{lang.overwritten}: {n["overwr"]}'
            if not values["-OUT_SKIP-"]
            else f'\n{lang.skipped}: {n["skipped"]}'
        )
    sg.popup_ok(summary_text, title=f"{lang.summary} {job}")

    return out

# make directory tree used for sg.Tree
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

# get analysis number 
def get_nums(path):
    files = os.listdir(path)
    return files, sorted(list(
        set([file[-9:-4] for file in files if re.fullmatch(".{2,3}\d{5}\.dat", file)])
    ), reverse=True)

def get_files(path, num_0, num_1, chunk=0, n_files= 100):
    if not path:
        return []
    files, nums = get_nums(path)
    nums = [num for num in nums if (num_0 <= num <= num_1)]

    if len(nums) > n_files:
        nums = nums[chunk*n_files:(chunk+1)*n_files]

    signals = {
        num: {
            "name": [get_ana_name(fname=file, input_folder=path) for file in files if num in file and file.endswith(".dat")][0] , 
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
            dat["name"],
            time.strftime("%Y-%m-%d", time.localtime(dat["time"])),
            *["x" if p.upper() in dat["files"] else "" for p in FILE_PREFIXES],
        ]
        for num, dat in signals.items()
    ]


def sort_table(values: Iterable, col: int, reverse: bool):
    return sorted(values, key=lambda x: x[col], reverse=reverse)


def draw_plot(window: sg.Window, values: Mapping, num: str, offs: Mapping):
    # https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib_Embedded_Toolbar.py
    # ------------------------------- PASTE YOUR MATPLOTLIB CODE HERE
    path = values["-F_TREE-"][0]
    selected = (
        values["-OC_P-"],
        values["-UV_P-"],
        values["-UV2_P-"],
        values["-T_P-"],
    )
    files = os.listdir(path)
    fnames = [f'{prefix}{num}.dat' for prefix, select in zip(FILE_PREFIXES, selected) if select and f'{prefix}{num}.dat' in files]

    if fnames:
        df = convert(fnames, path, offs, corr=values["-CORR-"])

    else:
        return

    lss = {"OC": "solid", "UV": "dashdot", "UV2": "dashed", "t": "dotted"}
    with plt.ion():
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
        plt.show(block=True)

    # ------------------------------- Instead of plt.show()
    # draw_figure_w_toolbar(
    #     window["-FIGURE-"].TKCanvas, fig, window["-CONTROLS-"].TKCanvas
    # )


def clean_figure(num=1):
    global legend_elements, colors, in_graph
    in_graph = set()
    colors = cycle([color["color"] for color in rcParams["axes.prop_cycle"]])
    legend_elements = {"handles": [], "labels": []}
    with plt.ion():
        fig = plt.figure(num)
        fig.clear(keep_observers=True)


def get_int_bounds_from_file(path):
    header = pd.Index([lang.start, lang.end, lang.name])
    df = (
        pd.read_excel(path, header=0)
        if not path.endswith(".csv")
        else pd.read_csv(path)
    )
    df.columns = [col.capitalize() for col in df.columns]
    if header.intersection(df.columns).size != header.size:
        return None

    for col in df.columns:
        if col.capitalize not in header:
            continue
        if col.capitalize != lang.name:
            df[[col]] = df[[col]].applymap(lambda x: to_float(x))
            df.dropna(inplace=True)

    return df[header].values.tolist()


def to_float(x):
    out = pd.to_numeric(x, errors="coerce")
    if pd.isna(out):
        return pd.NA
    else:
        return out


def update_ftree(window: sg.Window, values: list, path: str, reverse: bool):
    num_0, num_1 = values["-FILE_SEL_COMBO_0-"], values["-FILE_SEL_COMBO_1-"]
    _, nums = get_nums(path)
    nums = [num for num in nums if (num_0 <= num <= num_1)]

    MAX_DIR = values['-MAX_DIR-']
    TOTAL = len(nums)
    PAGES = int(TOTAL / MAX_DIR) +1
    PAGE = min(PAGES, int(values['-PAGE-']))
    window['-PAGE-'].update(range=(1, PAGES))
    data = get_files(path,
                    values["-FILE_SEL_COMBO_0-"], 
                    values["-FILE_SEL_COMBO_1-"],  
                    chunk=PAGE-1, 
                    n_files=MAX_DIR)
    window["-T_FILES-"].update(sort_table(data, 0, reverse=reverse))
    window['-PAGE_RANGE-'].update(f'{PAGE} / {PAGES}')

