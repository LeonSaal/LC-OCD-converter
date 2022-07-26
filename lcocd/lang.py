from dataclasses import dataclass


@dataclass
class EN:
    sel_conv = "Select files to convert"
    sel_folder = "Select folder"
    incl_sub = "Include subdirectories"
    sel_dest = "Select destination folder"
    skip = "Skip if destination file already exists"
    same_folder = "Source folder"
    diff_folder = "different folder"
    keep_sub = "Keep folder structure"
    settings = "Settings"
    incl_signal = "Include:"
    corr = "Corrections:"
    lin_corr = "Linear baseline-correction"
    int = "Integrate"
    add = "add"
    delete = "delete"
    mod = "modify"
    convert = "convert"
    exit = "exit"
    enter_fname = "Please enter a file name"
    start = "start"
    name = "name"
    end = "end"
    out_fname = "Destination file:"
    input_warning = (
        f"{start} and {end} must be both positive numbers and {start} < {end}!"
    )
    fopen_warning = (
        "is openened by another program.\n To proceed, close file or enter new name."
    )
    prog_name = "LC-OCD converter"
    info = "info"
    about = "about"
    contact_info = (
        "Leon Saal\nleon.saal@uba.de\nhttps://github.com/LeonSaal/LC-OCD-converter\n"
    )
    file = "files"
    file_prev = "file preview"
    cl = "clear"
    tip_ftable = "click row to add to graph below. Click table header to sort table"
    tip_itable = "click on row to modify/delete, below to add rows"
    tip_ftree = "click on element to list files"
    folder_browser = "browse folders"
    fig = "figure"
    default_int = "load default"
    bounds_int = "Integration bounds"
    load_int = "load from file"
    err_int_load = 'Error loading from file. File must contain "start", "end" and "name" in header.'
    warn = "Warning"
    fout_exist = "already exists!"
    overwr = "Overwriting"
    curr_sample = "Current sample:"
    convo = "conversion"
    sample = "sample"
    signal = "signal"
    no_file_warning = "No files found in "
    min = "minutes"
    time = "time"
    defa_int_bounds = "Default integration bounds based on:"
    proj = "Visit Project online:"
    contact = "Contact:"
    fmt = 'Output format:'
    align='align'
    reset = 'reset'
    curs='cursor'
    offs = 'offset'
    browse_files = 'browse files'

lang = EN
