rem *** Used to create a Python exe 

rem ***** get rid of all the old files in the build folder
rd /S /Q build
rd /S /Q dist

rem ***** create the exe
python setup.py py2exe >make_exe.log

pause "Start kopiering"

xcopy R-2.11.1 dist\R-2.11.1\ /S

rem **** pause so we can see the exit codes
pause "done...hit a key to exit"
