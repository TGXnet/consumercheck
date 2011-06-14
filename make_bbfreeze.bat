rem *** Used to create a Python exe

rem ***** get rid of all the old files in the build folder
rd /S /Q consumercheck-0.4.1
rem pause "removed"

rem ***** create the exe
python bbfreeze-cc.py>bbfreeze-cc.log
rem pause "freezed"

rem *** copy files
xcopy R-2.11.1 consumercheck-0.4.1\R-2.11.1\ /S /Q
xcopy datasets consumercheck-0.4.1\datasets\ /S /Q

rem *** Remove not used libaries
del /Q consumercheck-0.4.1\QtWebKit4.dll
del /Q consumercheck-0.4.1\QtGui4.dll
del /Q consumercheck-0.4.1\PyQt4.QtGui.pyd
del /Q consumercheck-0.4.1\QtCore4.dll
del /Q consumercheck-0.4.1\PyQt4.QtCore.pyd
del /Q consumercheck-0.4.1\QtNetwork4.dll
del /Q consumercheck-0.4.1\_ssl.pyd
del /Q consumercheck-0.4.1\PIL._imaging.pyd
del /Q consumercheck-0.4.1\PyQt4.QtWebKit.pyd

rem rd /S /Q consumercheck-0.4.1\traitsbackendqt-3.5.0-py2.6.egg

rem **** pause so we can see the exit codes
pause "done...hit a key to exit"
