# LC-OCD-converter
Tool for summarizing and previewing data from LC-OCD-UV by <doc-labor.de>.
Raw data with filenames `<prefix>000000.dat` are summarized to `000000.xlsx` with `<prefix>` as columns.

Optionally, the signals can be baseline-corrected (linear) and integrated between custon bounds.

## Installation
With `conda` and `pip`:
`conda create -n <YOUR_ENV> python=3.10.4`

`pip install git+https://github.com/LeonSaal/LC-OCD-converter.git`

## Usage
After installation, run `run.py` from the same environment.
`python run.py`

By doing so, `gui()` is imported from the package and executed.