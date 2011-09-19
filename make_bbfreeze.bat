rem *** Used to create a Python exe

rem ***** get rid of all the old files in the build folder
rem rd /S /Q consumercheck-0.5.0
rem pause "removed"

rem ***** create the exe
python bbfreeze-cc.py>bbfreeze-cc.log
rem pause "freezed"

rem *** Remove not used libaries
del /Q consumercheck-0.5.0\QtWebKit4.dll
del /Q consumercheck-0.5.0\QtGui4.dll
del /Q consumercheck-0.5.0\PyQt4.QtGui.pyd
del /Q consumercheck-0.5.0\QtCore4.dll
del /Q consumercheck-0.5.0\PyQt4.QtCore.pyd
del /Q consumercheck-0.5.0\QtNetwork4.dll
del /Q consumercheck-0.5.0\_ssl.pyd
del /Q consumercheck-0.5.0\PIL._imaging.pyd
del /Q consumercheck-0.5.0\PyQt4.QtWebKit.pyd

rem rd /S /Q consumercheck-0.5.0\traitsbackendqt-3.5.0-py2.6.egg

rem **** pause so we can see the exit codes
pause "done...hit a key to exit"
