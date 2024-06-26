from dataclasses import dataclass


@dataclass
class EN:
    sel_conv = "Input folder"
    sel_folder = "Select folder"
    sel_file = "Select file"
    incl_sub = "Include subdirectories"
    sel_dest = "Output folder"
    skip = "Skip if destination file already exists"
    same_folder = "Source folder"
    diff_folder = "different folder"
    keep_sub = "Keep folder structure"
    settings = "Settings"
    incl_signal = "Include"
    corr = "Corrections / Warnings"
    lin_corr = "Linear baseline-correction"
    int = "Integrate"
    add = "Add"
    delete = "Delete"
    mod = "Modify"
    convert = "Convert"
    exit = "Exit"
    fname = "File name"
    enter_fname = f"Please enter a {fname.lower()}"
    start = "Start"
    name = "Name"
    end = "End"
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
    file = "Files"
    file_prev = "File preview"
    cl = "Clear"
    tip_ftable = "Click row to add to graph below. Click table header to sort table"
    tip_itable = "Click on row to modify/delete, below to add rows"
    tip_ftree = "Click on element to list files"
    tip_align = "Click row to select for alignment."
    tip_ali_offs = "Adjust time offset between signals. Use cursor for better results."
    tip_reset = "Program restart necessary."
    folder_browser = "Browse folder"
    fig = "Figure"
    default_int = "Load default"
    bounds_int = "Integration bounds"
    load_int = "Load from file"
    err_int_load = 'Error loading from file. File must contain "start", "end" and "name" in header.'
    warn = "Warning"
    fout_exist = "already exists!"
    overwr = "Overwriting"
    curr_sample = "Current sample:"
    convo = "Conversion"
    sample = "Sample"
    signal = "Signal"
    no_file_warning = "No files found in "
    min = "minutes"
    time = "Time"
    defa_int_bounds = "See default integration bounds"
    proj = "Visit Project online"
    contact = "Contact"
    fmt = "Output format"
    align = "Align"
    reset = "Reset"
    curs = "Cursor"
    offs = "Offset"
    browse_files = "Browse files"
    sat = "Saturation warning"
    mail = "leon.saal@uba.de"
    project_link = "https://github.com/LeonSaal/LC-OCD-converter"
    int_bounds_link = "https://doi.org/10.1016/j.watres.2007.05.029"
    summary = "Summary"
    skipped = "Skipped files"
    overwritten = "Overwritten files"
    total = "Total files"
    oc_warning = "OC saturation"
    page = 'Page'
    files_per_page = 'Files per page'
    file_selection = 'Select file range'
    from_ = 'from: '
    to = 'to: '
    num = "#"
    cont="Continue"
    intfname = "Integrals"


lang = EN
