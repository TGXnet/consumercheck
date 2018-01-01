@echo on
REM	--specpath=dist ^
REM	--hiddenimport=hoggorm ^
REM	--add-data="docs-user/build/html;help-docs" ^
REM 	--debug ^
pyinstaller.exe ^
	--log-level=WARN ^
	--clean ^
	--noconfirm ^
	--onedir ^
	--console ^
	--icon=win-cc.ico ^
	--name=ccwin ^
	--add-data="ConsumerCheck/*.png;." ^
	--add-data="ConsumerCheck/*.svg;." ^
	--add-data="ConsumerCheck/graphics;." ^
	--add-data="ConsumerCheck/VERSION.txt;." ^
	--add-data="ConsumerCheck/about.tmpl;." ^
	--add-data="Rdist/R-3.3.1;R-3.3.1" ^
	--additional-hooks-dir=pyi-hooks ^
	--runtime-hook=pyi-rthook_pyqt4.py ^
	--workpath=build ^
	--distpath=dist ^
	--path=ConsumerCheck ^
	ConsumerCheck\cc_start.py
