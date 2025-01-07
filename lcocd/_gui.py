import json
# https://stackoverflow.com/a/1447581
from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.2f')
import os
import os.path
import posixpath as pxp
import re
import time
import tkinter as tk
import tkinter.messagebox as msg
import tkinter.ttk as ttk
from functools import partial
from itertools import cycle, islice
from pathlib import Path
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename

import matplotlib
import matplotlib.patches
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import rcParams
from matplotlib.lines import Line2D
from matplotlib.axes import Axes

matplotlib.use("TkAgg")

from ._func import convert, get_ana_name, integrate, save_data

FILE_PREFIXES = ['OC_', 'uv_', 'uv2', 't_']
SIGNALS = ["OC", "UV", "UV2", "t"]

FILE_FORMATS = [".csv", ".xlsx" , ".xls", ".ods"]
COLORS = cycle([color["color"] for color in rcParams["axes.prop_cycle"]])

DEFAULT_INT_BOUNDS = {
     "Biopolymers": [30, 45],
     "Humic substances": [45, 59],
     "Low-molecular-weight acids": [59, 66],
     "Low-molecular-weight neutrals": [66, 120]
}


class EdiTable(tk.Frame):
    def __init__(self, parent, vals, *args, **kwargs) -> None:
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.int_bounds = vals
        self.create_widgets(parent)
        self.create_binds()
        

    def create_widgets(self, parent):
        frame = ttk.Frame(parent)
        frame.grid()
        self.columns = ("Name", "Start", "End")
        self.entry_val = tk.StringVar()
        self.entry_coord = (None, None)
        def set_val(P):
            if not self.entry_coord[1].endswith("1"):
                try:
                    float(P)
                except ValueError:
                    P=""
            return True

        update_val = self.register(set_val)
        self.tree = ttk.Treeview(frame, columns=self.columns, show="headings")
        self.entry = ttk.Entry(frame, textvariable=self.entry_val, validatecommand=(update_val, "%P"), validate="focusout")
        for col, width in zip(self.columns, [200, 70, 70]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, stretch=tk.YES, minwidth=width)
        for key, val in self.int_bounds.items():
            self.tree.insert("", tk.END, values=[key, *val])
        self.tree.grid()

    def create_binds(self):
        def load_defaults():
            self.tree.delete(*self.tree.get_children())
            for name, bounds in DEFAULT_INT_BOUNDS.items():
                self.tree.insert("", tk.END, values = [name, *bounds])

        menu = tk.Menu(self.tree)
        menu.add_command(label="Load defaults", command=load_defaults)
        self.tree.bind("<Double-Button-1>", self.place_entry)
        self.tree.bind("<Delete>", self.del_row)
        self.tree.bind("<Button-3>", lambda e: menu.post(e.x, e.y))
        self.entry.bind("<KeyPress-Tab>", self.place_entry)
        self.entry.bind("<Shift-KeyPress-Tab>", self.place_entry)
        self.tree.bind("<FocusIn>", self.set_val)

    def place_entry(self, event:tk.Event=None):
        if event.keysym=="Tab":
            self.set_val()
            row, column = self.entry_coord
            column_offset = -1 if event.state==9 else 1
            column_index = int(column[-1])+column_offset
            column_index = min(max(1, column_index), 3)
            column = f"#{column_index}"
        else:
            x, y = event.x, event.y
            row, column = self.tree.identify_row(y), self.tree.identify_column(x)
            
        self.new_entry_coord = (row, column) 
        if not self.tree.bbox(*self.new_entry_coord):
            self.tree.insert("", tk.END, values=["Name", "0", "0"])
            return
        
        cx, cy, cw, ch = self.tree.bbox(*self.new_entry_coord)
        self.entry.place(x=cx, y=cy, width=cw, height=ch)
        self.entry_val.set(value=self.get_val(*self.new_entry_coord))
        self.entry_coord = self.new_entry_coord
        self.update_entry()
        return("break")

    def update_entry(self, event=None):
        self.entry.icursor(tk.END)
        self.entry.select_range(0, tk.END)

    def get_val(self, row, column):
        return self.tree.item(row)["values"][int(column.replace("#",""))-1]
    
    def set_val(self, event=None):
        val = self.entry.get()
        if not self.entry_coord[0]:
            return
        if self.entry_coord[1] == "#0":
            return
        if not self.entry_coord[1].endswith("1"):
            try:
                float(val)
            except ValueError:
                val=""

        self.tree.set(*self.entry_coord, value=val)
        self.entry.place_forget()

    def del_row(self, event=None):
        iid = self.tree.focus()
        if iid:
            self.tree.delete(iid)

class App(tk.Frame):
    def __init__(self, parent):
        parent.option_add('*tearOff', False)
        parent.protocol("WM_DELETE_WINDOW", self.on_closing)
        # parent.wm_attributes('-transparentcolor', '#ab23ff')
        self.parent = parent
        self.create_vars()
        self.create_menu(parent)
        self.create_widgets(parent)  
        self.restore_state()

    def create_menu(self, parent):
        menu = tk.Menu(parent)
        parent.config(menu=menu)
        menu_set = tk.Menu(menu)
        menu_inp = tk.Menu(menu_set)
        menu_inp_signals = tk.Menu(menu_inp)
        menu_out = tk.Menu(menu_set)
        menu_out_type = tk.Menu(menu_out)
        menu_corr = tk.Menu(menu_set)       
        menu.add_cascade(menu=menu_set, label="Settings")

        # input
        menu_set.add_cascade(menu=menu_inp_signals, label="Input")
        for SIGNAL in SIGNALS:
            menu_inp_signals.add_checkbutton(label=f"use {SIGNAL!r} signal", variable=eval(f"self.include_{SIGNAL}"))

        # output
        menu_set.add_cascade(menu=menu_out, label="Output")
        menu_out.add_checkbutton(label="Skip if file already exists", variable=self.settings_skip_exist)
        menu_out.add_cascade(menu=menu_out_type, label="File format")
        for file_format in FILE_FORMATS:
            menu_out_type.add_radiobutton(label=file_format, variable=self.settings_file_format)

        # integration
        menu_out.add_command(label="Modify integration bounds", command=self.set_integration_bounds)
 
        # corrections/warnings
        menu_out.add_cascade(menu=menu_corr, label="Corrections / warnings")
        menu_corr.add_checkbutton(label="Linear baseline correction", variable=self.settings_correct)
        menu_corr.add_checkbutton(label="Auto-align traces", variable=self.settings_align)
        menu_corr.add_separator()
        menu_corr.add_checkbutton(label = "Enable saturation warning", variable=self.settings_satur)
        menu_corr.add_command(label="Set saturation thresholds", command=self.set_au_thresh)

        # delete
        menu_set.add_separator()
        menu_set.add_command(label="Load settings", command=self.load_settings)
        menu_set.add_command(label="Save settings", command=self.save_settings)

        # about
        menu.add_command(label="About", command=self.about)

    def create_vars(self):
        #paths
        self.input_path = tk.StringVar(value="")
        self.output_path = tk.StringVar(value="")
        self.save_path = "settings.json"

        # progress
        self._progress_text = tk.StringVar(value="")
        self._progress_val = tk.IntVar(value=0)
        for SIGNAL in SIGNALS:
            self.__setattr__(f"prev_{SIGNAL}", tk.BooleanVar(value=False if SIGNAL == "t" else True))
            self.__setattr__(f"include_{SIGNAL}", tk.BooleanVar(value=False if SIGNAL == "t" else True))
            self.__setattr__(f"au_thresh_{SIGNAL}", tk.StringVar(value="0"))
            self.__setattr__(f"au_thresh_use_{SIGNAL}", tk.BooleanVar(value=False))
        self.prev_int_bounds = tk.BooleanVar(value=False)

        # settings
        self.settings_correct = tk.BooleanVar(value=True)
        self.settings_satur = tk.BooleanVar(value=False)
        self.settings_file_format = tk.StringVar(value=FILE_FORMATS[0])
        self.settings_skip_exist = tk.BooleanVar(value=True)
        self.settings_num_rows = tk.IntVar(value=25)
        self.settings_align = tk.BooleanVar(value=True)

        # preview
        self.prev_legend_elements = {"handles": [], "labels": []}
        self.prev_in_graph = set()
        self.xranges = []
        self.tmp_xrange = {}

        # integration
        self.int_bounds = {}

        # table edit
        self._browser_table_entry_val = tk.StringVar(value="")
        self.browser_table_iid = None

    def create_widgets(self, parent):
        tk.Frame.__init__(self, parent, borderwidth=9, relief="flat")

        input_frame = tk.LabelFrame(parent, text="")
        input_pathlab = tk.Label(input_frame, textvariable=self.input_path, relief=tk.RIDGE, justify="left", width=70)
        input_pathchoose = ttk.Button(input_frame, text="Input path", command=self.set_input_path)
        output_pathlab = tk.Label(input_frame, textvariable=self.output_path, relief=tk.RIDGE, justify="left")
        output_pathchoose = ttk.Button(input_frame, text="Output path", command=self.set_output_path)

        browser_frame = tk.LabelFrame(parent, text="Browse files")
        self.browser_paths = ttk.Treeview(browser_frame)
        
        
        self.browser_scroll = tk.Scrollbar(browser_frame)
        columns = ("#", "Name", "Date", *SIGNALS)
        self.browser_table = ttk.Treeview(browser_frame, 
                                          columns=columns, 
                                          show="headings",
                                          yscrollcommand=self.browser_scroll.set)
        for column, width, stretch in zip(
            columns, [40, 150, 70]+ [30]*4, 
            [tk.NO, tk.NO]+[tk.YES]*5):
            self.browser_table.heading(column, text=column)
            self.browser_table.column(column, width=width, stretch=stretch, minwidth=width)

        self.browser_table_entry = ttk.Entry(self.browser_table, textvariable=self._browser_table_entry_val)

        self.browser_menu = tk.Menu(self.browser_table)
        for option in ["select all", "convert", "integrate", "edit name"]:
            self.browser_menu.add_command(label=option, command=eval("self."+option.replace(" ", "_")))
        
        browser_menu_prev = tk.Menu()
        browser_menu_files = tk.Menu()
        for SIGNAL in SIGNALS:
            browser_menu_prev.add_checkbutton(label=f"show {SIGNAL!r}", variable = eval(f"self.prev_{SIGNAL}"))
        browser_menu_prev.add_checkbutton(label="show integration bounds", variable = self.prev_int_bounds)
        browser_menu_prev.add_separator()
        browser_menu_prev.add_command(label="clear preview", command=self.clear_preview)
        self.browser_menu.add_cascade(menu=browser_menu_prev, label="preview options")
        self.browser_menu.add_cascade(menu=browser_menu_files, label="files per page")
        for rows in [25, 50, 100, 250]:
            browser_menu_files.add_radiobutton(label=rows, variable=self.settings_num_rows)
        progress_lab = ttk.Label(browser_frame, textvariable=self._progress_text)
        self.progress_bar = ttk.Progressbar(browser_frame, 
                                            variable=self._progress_val, 
                                            orient=tk.HORIZONTAL, 
                                            mode="determinate")
    
        # layout
        input_frame.grid(column=0, row=0, sticky=tk.W+tk.E)
        input_pathchoose.grid(column=0, row=0, sticky=tk.W+tk.E)
        input_pathlab.grid(column=1, row=0, sticky=tk.W)
        output_pathchoose.grid(column=0, row=1, sticky=tk.W)
        output_pathlab.grid(column=1, row=1, sticky=tk.W+tk.E)

        browser_frame.grid(column=0, row=2, sticky=tk.W+tk.E)
        self.browser_paths.grid(column=0, row=0, sticky=tk.W+tk.E+tk.S+tk.N)
        self.browser_table.grid(column=1, row=0, sticky=tk.W+tk.E)
        self.browser_scroll.grid(column=2, row = 0, sticky=tk.S+tk.N)
        
        progress_lab.grid(row=1, column=0, sticky=tk.W)
        self.progress_bar.grid(row=1, column=1, columnspan=1, sticky=tk.W+tk.E)

        # events
        self.browser_paths.bind("<Double-Button-1>", self.browser_change_path)
        self.browser_table.bind("<Button-3>", self.right_click_menu)
        self.browser_table.bind("<Double-Button-1>", self.preview)
        self.browser_table.bind("<Control-KeyPress-a>", lambda e: self.select_all())
        self.browser_scroll['command'] = self.browser_scroll_cmd
        self.browser_table_entry.bind("<FocusOut>", self.browser_table_edit)
        self.browser_table_entry.bind("<Escape>", self.browser_table_edit)
        self.browser_table_entry.bind("<Return>", self.browser_table_edit)
        self.browser_table.bind("<MouseWheel>", self.browser_table_edit)
        self.browser_table_entry.bind("<KeyPress-Up>", self.browser_table_neighbor_cell)
        self.browser_table_entry.bind("<KeyPress-Down>", self.browser_table_neighbor_cell)

        for w in (self, parent):
            w.rowconfigure(0, weight=1)
            w.columnconfigure(0, weight=1)
    
    def browser_table_neighbor_cell(self, event=None):
        if event.keysym == "Down":
            neighbor_iid = self.browser_table.next(self.browser_table_iid)
        if event.keysym == "Up":
            neighbor_iid = self.browser_table.prev(self.browser_table_iid)
        if not neighbor_iid:
            return
        self.browser_table.selection_set([neighbor_iid])
        self.browser_table.set(self.browser_table_iid, column="#2", value=self._browser_table_entry_val.get())
        self.browser_table_iid = neighbor_iid
        self.edit_name(event)

    def right_click_menu(self, event=None):
        if len(self.browser_table.get_children())==0:
            return
        self.browser_menu.post(event.x_root, event.y_root)

    def edit_name(self, event=None):
        if event:
            iid = self.browser_table_iid
        else:
            iid = self.browser_table.focus()

        if not self.browser_table.bbox(iid, column = "#2"):
            return
        cx, cy, cw, ch = self.browser_table.bbox(iid, column = "#2")
        self.browser_table_entry.place(x=cx, y=cy, width=cw, height=ch)
        self._browser_table_entry_val.set(value=self.browser_table.item(iid)["values"][1])
        self.browser_table_entry.icursor(tk.END)
        self.browser_table_entry.select_range(0, tk.END)
        self.browser_table_entry.focus_set()
        self.browser_table_iid = iid

    def browser_table_edit(self, event=None):
        if not self.browser_table_iid:
            return
        self.browser_table.set(self.browser_table_iid, column="#2", value=self._browser_table_entry_val.get())
        self.browser_table_entry.place_forget()
        self.browser_table.focus_set()

    def restore_state(self):
        if not os.path.exists(self.save_path):
            return
        
        with open(self.save_path, "r") as file:
            settings = json.load(file)
        
        for key, val in settings.items():
            if not key in self.__dict__:
                continue
            
            if isinstance(self.__dict__[key], tk.Variable):
                self.__dict__[key].set(val)
            else:
                self.__dict__[key] = val
        
        if os.path.exists(self.input_path.get()):
            self.browser_update_paths()
            self.browser_update_files_in_path()
            self.browser_update_tbl()
        else:
            self.input_path.set("")

    def save_settings(self):
        outfile = asksaveasfilename(defaultextension=".json", filetypes=[("json", "*.json")], initialfile="settings.json", initialdir=Path(__file__))
        if outfile:
            self.save_path=outfile
            self.save_state()

    def load_settings(self):
        infile = askopenfilename(defaultextension=".json", filetypes=[("json", "*.json")], initialfile="settings.json", initialdir=Path(__file__))
        if infile:
            self.save_path=infile
            self.restore_state()

    def on_closing(self, event=None):
        self.save_state()
        plt.close("all")
        self.parent.destroy()

    def save_state(self):
        out = {}
        for key, val in self.__dict__.items():
            if key.startswith("_"):
                continue
            if isinstance(val, tk.Variable):
                out[key] = val.get()
            elif key in ["offs", "int_bounds"]:
                out[key] = val

        with open(self.save_path, "w") as file:
            json.dump(out, file, indent=4)

    def delete_state(self, event=None):
        if os.path.exists(self.save_path):
            os.remove(self.save_path)


    def about(self):
        window = tk.Toplevel()
        window.title("About")
        text = """
        Developed by:\tLeon Saal\n
        Site:\t\t\tgithub.com/LeonSaal/LC-OCD-converter\n
        Last Modified:\tLAST_MODIFIED
        """
        ttk.Label(window, text=text).grid()

    def browser_scroll_cmd(self, *scroll):
        scroll_end = 0.95
        if self.browser_scroll.get()[1] > scroll_end:
            intable = len(self.browser_table.get_children())
            self.browser_update_tbl()
            self.browser_scroll.set(intable * scroll_end**2, intable + self.settings_num_rows.get())
        self.browser_table.yview(*scroll)

    def browser_update_tbl(self):
        path = self.input_path.get()
        for num, signals in next(self.yield_files(),[]):
            file = f"{signals[0]}{num}.dat"
            fullpath = os.path.join(path, file)
            ctime = time.localtime(pxp.getctime(fullpath))
            date = time.strftime("%Y-%m-%d", ctime)
            name = get_ana_name(file, path)
            sigs_avail = ["x" if signal in FILE_PREFIXES else "" for signal in signals]
            self.browser_table.insert("", tk.END, text=path, values=[num, name, date]+sigs_avail)

    def browser_update_files_in_path(self):
        path = self.input_path.get()
        files = os.listdir(path)
        analyses = {}
        for file in files:
            if not re.fullmatch(r".{2,3}\d{5}\.dat", file):
                continue
            num = file[-9:-4]
            prefix = file[0:-9]
            if num not in analyses:
                analyses[num]=[prefix]
            else:
                analyses[num].append(prefix)
        self.analyses = ((key, value) for key, value in sorted(analyses.items(), key=lambda item: item[0], reverse=True))

    

    # https://stackoverflow.com/a/51446512
    def yield_files(self):
        while True:
            chunk= [*islice(self.analyses, 0, self.settings_num_rows.get())]
            if chunk:
                yield chunk
            else:
                break

    def browser_update_paths(self):
        path = Path(self.input_path.get())
        self.browser_paths.delete(*self.browser_paths.get_children())
        self.browser_paths.insert("", tk.END,path.as_posix(), text=path.name, values =[])

        for root, _, _ in os.walk(path):
            parent = Path(root).parent.as_posix()
            child = Path(root)
            name = child.name
            if child != path:
                self.browser_paths.insert(parent, tk.END, child.as_posix(), text=name, values=[])

    def set_input_path(self):
        path = askdirectory()
        if not path:
            return
        self.input_path.set(path)
        self.browser_update_paths()
        self.browser_update_files_in_path()
        self.browser_update_tbl()

    def set_output_path(self):
        p = askdirectory(initialdir=self.input_path)
        self.output_path.set(p if p else "")  

    def browser_change_path(self, event=None):
        self.browser_table.delete(*self.browser_table.get_children())
        path = self.browser_paths.focus()
        if path:
            self.browser_update_tbl()

    def convert(self):
        iids = self.browser_table.selection()
        if not iids:
            return
        items = [self.browser_table.item(iid) for iid in iids]
        n_items = len(items)
        self.progress_bar.configure(maximum=n_items)
 
        output_folder = self.output_path.get()
        if not output_folder:
            msg.showwarning(title="Warning", message="Specify output path first!")
            return
        input_folder = items[0]["text"]

        # list files in outputfolder to check for skippable files
        input_files = os.listdir(input_folder)
        out_files = os.listdir(output_folder)

        #setup output
        n = {"skipped": 0, "overwr": 0, "total": 0}
        for i, item in enumerate(items, start=1):
            self.parent.update_idletasks()
            n["total"] += 1
            counter = self._progress_val.get() +1
            self._progress_val.set(counter)
            self._progress_text.set(f"{i} / {n_items} ({i/n_items:.0%})")
    
            num = item["values"][0]
            ananame = item["values"][1]
            fnames = [f'{prefix}{num}.dat' for prefix in FILE_PREFIXES if f'{prefix}{num}.dat' in input_files]
            if not fnames:
                continue

            f_out = f"{num}_{ananame}"

            # check wheteher to skip or overwrite output file
            if (f"{f_out}{self.settings_file_format.get()}" in out_files):
                if self.settings_skip_exist.get():
                    n["skipped"] += 1
                    continue
                else:
                    n["overwr"] += 1

            if fnames:
                df = convert(fnames, input_folder, self.settings_align.get(), corr=self.settings_correct.get())
                selected = [SIGNAL  for SIGNAL in SIGNALS if self.__dict__[f"include_{SIGNAL}"].get()] 
                df = df[selected]
                save_data(df, output_folder, f_out, self.settings_file_format.get())

        # give summary
        message = f'Files total: {n["total"]}'+(
            f'\nFiles overwriten: {n["overwr"]}'
            if not self.settings_skip_exist.get()
            else f'\nFiles skipped: {n["skipped"]}'
        )
        msg.showinfo("Conversion complete", message=message)
        self._progress_val.set(0)

    def integrate(self):
        iids = self.browser_table.selection()
        if not iids:
            return
        
        if len(self.int_bounds) ==0:
            msg.showwarning("No bounds", "Please specify integration bounds!\n\nNote:\n - double-click below last row to add row\n - double-click cell to edit\n - press <Delete> to remove row")
            self.set_integration_bounds()
            return

        items = [self.browser_table.item(iid) for iid in iids]
        n_items = len(items)
        self.progress_bar.configure(maximum=n_items)
        file_formats = sorted(FILE_FORMATS, key=lambda fmt: fmt==self.settings_file_format.get(), reverse=True)
        file_formats = ((f"{fmt.replace('.', '')}", f"*{fmt}") for fmt in file_formats)
        initialdir = self.output_path.get() if self.output_path.get() else self.input_path.get()
        outfile = asksaveasfilename(initialdir=initialdir, 
                                    initialfile="Integrals", 
                                    filetypes=file_formats,
                                    defaultextension=file_formats)
        if not outfile:
            return
        
        out = pd.DataFrame()
        input_folder = items[0]["text"]
        input_files = os.listdir(input_folder)

        #setup output
        n = {"skipped": 0, "overwr": 0, "total": 0}
        for i, item in enumerate(items, start=1):
            self.parent.update_idletasks()
            n["total"] += 1
            counter = self._progress_val.get() +1
            self._progress_val.set(counter)
            self._progress_text.set(f"{i} / {n_items} ({i/n_items:.0%})")
    
            num = item["values"][0]
            ananame = item["values"][1]
            fnames = [f'{prefix}{num}.dat' for prefix in FILE_PREFIXES if f'{prefix}{num}.dat' in input_files]
            if not fnames:
                continue

            if fnames:
                df = convert(fnames, input_folder, align=self.settings_align.get(), corr=self.settings_correct.get())
                selected = [SIGNAL for SIGNAL in SIGNALS if self.__dict__[f"include_{SIGNAL}"].get()]    
                df = df[selected]
                if self.int_bounds:
                    integrals = pd.concat(
                        [integrate(df, self.int_bounds)],
                        keys=[(num, ananame)],
                        names=["Sample", "Name", "Signal"],
                    )
                    if self.settings_satur.get():
                        warning_text = ", ".join(
                            [
                                SIGNAL
                                for SIGNAL in SIGNALS
                                if ((SIGNAL in df) and (self.__dict__[f"au_thresh_use_{SIGNAL}"].get()) and (df[SIGNAL].max() > float(self.__dict__[f"au_thresh_{SIGNAL}"].get())))
                            ]
                        )
                        integrals["SATURATION_WARNING"] = warning_text

                    out = pd.concat([out, integrals], axis=0)

        self._progress_val.set(0)

        try:
            if outfile.endswith(".csv"):
                out.to_csv(outfile)
            else:
                out.to_excel(outfile)
        except OSError as e:
            msg.showerror(e.args[1], f"File {e.filename!r} can't be written.")

    def select_all(self):
        iids = self.browser_table.get_children()
        self.browser_table.selection_set(iids)

    def clear_preview(self, event=None):
        self.prev_in_graph = set()
        self.prev_colors = cycle([color["color"] for color in rcParams["axes.prop_cycle"]])
        self.prev_legend_elements = {"handles": [], "labels": []}
        with plt.ion():
            self.fig = plt.figure(1)
            self.fig.clear(keep_observers=True)
            plt.close()

    def modify_bounds(self, event=None):
        x= round(event.xdata, 1)
        if event.dblclick and event.key=="control+shift":
            self.int_bounds = {name:xrange for name, xrange in self.int_bounds.items() if not float(xrange[0]) < x < float(xrange[1])}
            self.draw_range_name(event)

        elif event.dblclick and event.key=="control":
            if len(self.tmp_xrange) <2:
                self.tmp_xrange[len(self.tmp_xrange)] = [x, self.ax.axvline(x, color="red", ls="dashed")]

            if len(self.tmp_xrange)==2:
                for val in self.tmp_xrange.values():
                    val[1].remove()
                self.int_bounds.update({f"Range {len(self.int_bounds)}": list(sorted([val[0] for val in self.tmp_xrange.values()]))})
                self.draw_range_name(event)
                self.tmp_xrange = {}
        plt.show()

    # draw integration ranges, in green if hovering over it
    def draw_range_name(self, event=None):
        if not event.xdata:
            return
        x = round(event.xdata, 2)

        for xrange in self.xranges:
            xrange.remove()
        self.xranges = []
        
        if self.curx in self.ax.get_children():
            self.curx.remove()

        if event.key=="control":
            self.curx = self.ax.axvline(x, color="red", ls="dashed")

        candidates = {name: (start, end) for name, (start, end) in self.int_bounds.items() if start < x < end}
        candidates_sort = sorted(candidates.items(), key = lambda item: item[1][0]-item[1][1])
        if candidates_sort:
            title, (start, end) = candidates_sort.pop()
        else:
            plt.show()
            return
            
        xranges = sorted([xrange for xrange in self.int_bounds.values()], key=lambda xr: xr[0]==start and xr[1]==end)
        for i, xrange in enumerate(xranges):
            color  = "white" if i < (len(xranges) -1) or not title else "#B3FFCA"
            self.xranges.append(self.fig.gca().axvspan(*xrange, facecolor=color, edgecolor=None, label=f"_{i}"))
        self.ax.set_title(title)

        plt.show()
        
    def update_preview(self, event=None):
        pass
        
    def preview(self, event = None):
        iid = self.browser_table.focus()
        if not iid:
            return
        
        item = self.browser_table.item(iid)
        path = item["text"]
        num = item["values"][0]
        name = item["values"][1]
        avails = item["values"][2:]

        if name in self.prev_legend_elements["labels"]:
            return
        
        fnames = [f'{prefix}{num}.dat' for prefix, avail in zip(FILE_PREFIXES, avails) if avail]

        if fnames:
            df = convert(fnames, path, align=self.settings_align.get(), corr=self.settings_correct.get())
            selected = [SIGNAL  for SIGNAL in SIGNALS if self.__dict__[f"prev_{SIGNAL}"].get()] 
            df = df[selected]
        else:
            return

        lss = {"OC": "solid", "UV": "dashdot", "UV2": "dashed", "t": "dotted"}
        with plt.ion():
            self.fig = plt.figure(1)
            # bind clear to closing of window
            self.fig.canvas.mpl_connect("close_event", self.clear_preview)
            self.ax = self.fig.gca()
            to_add = [column for column in df.columns]
            if not to_add:
                return

            self.prev_in_graph.update(to_add)
            color = next(COLORS)

            for plot in to_add:
                self.ax.plot(df[plot], color=color, ls=lss[plot])

            self.ylim = self.ax.get_ylim()

            if self.prev_int_bounds.get():
                # bind labeling of integration ranges
                self.curx = self.ax.axvline(color="red", ls="dashed", alpha=0)
                self.fig.canvas.mpl_connect("button_press_event", self.modify_bounds)
                self.fig.canvas.mpl_connect("motion_notify_event", self.draw_range_name)

            self.prev_legend_elements["handles"].append(
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
            self.prev_legend_elements["labels"].append(name)
            base_legend_elements = {
                "handles": [
                    Line2D([0], [0], color="black", ls=ls, markersize=10)
                    for key, ls in lss.items()
                    if key in self.prev_in_graph
                ],
                "labels": [SIGNAL for SIGNAL in SIGNALS if SIGNAL in self.prev_in_graph],
            }

            objs = self.fig.gca().findobj(matplotlib.legend.Legend)
            for obj in objs:
                obj.remove()

            self.ax.set_xlabel("Minutes")
            base_legend = self.ax.legend(**base_legend_elements, loc="upper left")
            self.ax.legend(**self.prev_legend_elements, loc="upper right")
            self.fig.gca().add_artist(base_legend)
            plt.show(block=False)
        
    def set_integration_bounds(self):
        window = tk.Toplevel(self)
        window.title("Integration Bounds")
        table = EdiTable(window, self.int_bounds)
        window.bind("<Escape>", window.destroy)
        def on_closing():
            iids = table.tree.get_children()
            items = [table.tree.item(iid) for iid in iids]
            self.int_bounds = {item["values"][0]: item["values"][1:] for item in items}
            window.destroy()
        window.protocol("WM_DELETE_WINDOW", on_closing)

    def set_au_thresh(self):
        # entry validation
        def check_float(inp, s):
            inp = inp.replace(",", ".")         
            try:
                if float(inp)>=0:
                    return True
                else:
                    return False
            except:
                return False
            
        window = tk.Toplevel(self)
        window.title("Set Saturation Thresholds")
        val_float = window.register(check_float)

        # switch entry state based on checkbutton
        def switch_state(signal):
            state = tk.NORMAL if self.__dict__[f"au_thresh_use_{signal}"].get() else tk.DISABLED
            entries[signal].configure(state=state)
        
        entries = {}
        for i, SIGNAL in enumerate(SIGNALS):
            ttk.Label(window, text=SIGNAL).grid(row=i, column=0, sticky=tk.W)
            ttk.Checkbutton(window, variable=eval(f"self.au_thresh_use_{SIGNAL}"), command=partial(switch_state, SIGNAL)).grid(row=i, column=1)
            state = tk.NORMAL if self.__dict__[f"au_thresh_use_{SIGNAL}"].get() else tk.DISABLED
            entry = ttk.Entry(window,validatecommand=(val_float, "%P", "%s"), validate="key", textvariable=eval(f"self.au_thresh_{SIGNAL}"), state=state)
            entry.grid(row=i, column=2)
            entries.update({SIGNAL: entry})
            
def gui():
    root = tk.Tk()
    root.title("LC-OCD-Converter")
    App(root)
    root.mainloop()

if __name__=="__main__":
    gui()