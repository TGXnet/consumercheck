rem *** Used to create a Python exe 

rem ***** get rid of all the old files in the build folder
rd /S /Q dist_bbfreeze

rem ***** create the exe
python bbfreeze-cc.py >make_bbfreeze.log

xcopy R-2.11.1 dist_bbfreeze\R-2.11.1\ /S /Q

rem **** pause so we can see the exit codes
pause "done...hit a key to exit"
