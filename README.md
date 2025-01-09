# LC-OCD-converter
Tool for summarizing and previewing data from LC-OCD-UV by [DOC-Labor](http://www.doc-labor.de).
Raw data with filenames `<prefix>000000.dat` are summarized to a single file with `<prefix>` as columns.

Optionally, the signals can be baseline-corrected (linear) and integrated between custom bounds.

# Installation
1. Download compiled executable for Windows from `/dist`
2. With `conda` and `pip`:

    ```
    conda create -n <YOUR_ENV> python=3.10.4
    conda activate <YOUR_ENV>
    pip install git+https://github.com/LeonSaal/LC-OCD-converter.git
    ```

# Usage
## Launching
1. Run Executable
2. In the installation environment: `python run.py`. By doing so, `gui()` is imported from the package and executed.

## Conversion
1. Select input path
2. Select output path
3. Select files to be converted in the *Browse files* table (*STRG + A* for all loaded or via *RIGHT CLICK* menu)
    > **Hint:**
    >
    > To load more files, scroll down the table to the end and/or edit *files per page* (*RIGHT CLICK* on table)
4. *RIGHT CLICK* $\rightarrow$ convert

## Integration
1. to 4. analog to [Conversion](#conversion)
    > **Hint:**
    >
    > Integration bounds can be modified via the menu *Settings* $\rightarrow$ *Output* $\rightarrow$ *Modify integration bounds*. 
    > *RIGHT CLICK* table and press *load defaults* to load bounds from [Haberkamp et al. (2007)](https://doi.org/10.1016/j.watres.2007.05.029).
    > 
    > Modify bounds with *DOUBLECLICK* on respective cell. Delete row with *DEL* and add row with *DOUBLECLICK* under last row.

## Preview
1. In *Browse files*-table *DOUBLECLICK* on row to open preview plot
2. Add more samples to same plot with 1.
3. Close window to reset or via *RIGHT CLICK* menu $\rightarrow$ *preview*

### Modifying bounds
1. Make sure under *RIGHT CLICK* menu $\rightarrow$ *preview options*, *show integration bounds* is checked
2. Hold *STRG* for x-cursor

    |Add|Delete|
    |-|-|
    | 3. *DOUBLECLICK* to add bounds|3. Also hold *SHIFT* |
    |4. Enter name in popup-window|4. *DOUBLECLICK* inside region you want to delete|

## Configuration
Via *Settings* menu:
|Menu item|Explanation|
|-|-|
|Input|Sets signals to be included in program output.|
|Output||
|> Skip if file already exists|Skip files during conversion.|
|> File format|choose from .csv, .xlsx, .xls and .ods.|
|> Modify integration bounds| See [Modifying bounds](#modifying-bounds).|
|> Corrections/warnings||
|>> Linear baseline correction|Shift values so 0 is the minimum.|
|>> Auto-align traces|Due to construction of device, the OC-signal lags behind the other signals. The bypass-peak from UV2 is used to align the traces.|
|>> Enable saturation warning|Set thresholds for signal intensities to mark samples from integration.|
|Load settings|Load settings from file other than `./settings.json`.|
|Save settings|Save settings to file other than `./settings.json`.|


