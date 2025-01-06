:: requires cloning of the repository and installation of pyinstaller

:: copy file with place-holder to parent dir
xcopy /y ".\lcocd\_gui.py" ".\"

:: specify place-holder and replacement
set "search=LAST_MODIFIED"
set replace=%date:.=-%

:: replace place-holder in file with ps file 
set "file=.\lcocd\_gui.py"
:: with help of internet...
:: https://www.reddit.com/r/PowerShell/comments/14v1nd1/powershell_from_a_batch_file_with_pipesquotes/
:: https://stackoverflow.com/questions/6037146/how-to-execute-powershell-commands-from-a-batch-file
:: https://stackoverflow.com/a/17144445
powershell -ExecutionPolicy Bypass -Command "& {(Get-Content '%file%').Replace('%search%', '%replace%') | Set-Content '%file%';}"

:: compile exe
pyinstaller --clean -F -n LCOCD_converter -w run.py 

:: move file with placeholder back
move /y ".\_gui.py" "lcocd"