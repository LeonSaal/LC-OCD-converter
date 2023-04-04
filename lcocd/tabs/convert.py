import PySimpleGUI as sg
from ..lang import lang

## Conversion tab
# Menu
menu_definition = [[lang.info, [lang.about]]]#[[lang.info, lang.about, lang.settings]]


# Conversion tab
tab_conversion = [
    [sg.Menu(menu_definition, key="-MENU-")],
    [sg.CBox(lang.incl_sub, default=False, key="-INP_SUBFOLDERS-")],
    [sg.CBox(lang.skip, default=True, key="-OUT_SKIP-")],
    [sg.CBox(lang.keep_sub, default=False, key="-OUT_SUBDIR-")],
    #[],
    #[sg.VPush()],
    #[sg.Frame(lang.corr, corrections_frame, expand_x=True)],
    #[sg.VPush()],
    #[sg.Frame(lang.int, int_frame, expand_x=True)],
    [sg.VPush()],
    [sg.Push(),sg.Button(lang.convert, key="-RUN-"), sg.Push()],
]