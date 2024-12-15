from typing import Iterable
import pandas as pd
import posixpath as pxp
import tkinter.messagebox as msg

NAMES = {"OC_": "OC", "UV_": "UV", "UV2": "UV2", "T_": "t"}

def get_ana_name(fname: str, input_folder: str):
    with open(pxp.join(input_folder, fname)) as f:
        return f.readline().strip()

def convert(fnames: Iterable, input_folder: str, align: bool, corr: bool = True):
    data = [
        pd.read_csv(
            pxp.join(input_folder, fname),
            sep=r"\s+",
            decimal=".",
            thousands=",",
            index_col=0,
            names=[NAMES[fname[:-9].upper()]],
            engine="python",
            skiprows=1,
            encoding="latin-1",
        )
        for fname in fnames
    ]

    df = pd.concat(data, axis=1)
    if corr:
        df = df.apply(lambda x: x.subtract(min(x), fill_value=min(x)))

    if align:
        max_bypass = df[df.index < 5][["OC", "UV"]].apply(lambda s: s.argmax(), axis=0).values
        ishift = max_bypass[1] - max_bypass[0]
        df["OC"] = df["OC"].shift(ishift)

    return df

def integrate_trapezoid(srs):
    return (pd.DataFrame({"dS":srs, "dt": srs.index})
            .diff()
            .shift(-1)
            .assign(S=srs)
            .assign(trap = lambda x: x.dt*(x.S+x.dS/2))
            .sum().trap)

def integrate(df, bounds):
    integrals = []
    for key, (start, end) in bounds.items():
        subset = df[(df.index >= float(start)) & (df.index < float(end))]
        integrals.append(subset.apply(lambda df: integrate_trapezoid(df)).rename(f"{key} ({start} - {end} Min)"))
    return pd.concat(integrals, axis=1)

def save_data(out: pd.DataFrame, output_folder: str, fname: str, ext: str):
    save = False
    while not save:
        path = pxp.join(output_folder, f"{fname}{ext}")
        try:
            out.to_excel(path, merge_cells=False) if ext != ".csv" else out.to_csv(path)
            save = True
        except PermissionError:
            msg.showwarning("Permissionerror",f"File {path} is used by another process.")
            if not fname:
                return