@echo on
rem --hidden-import MODULENAME ^
rem --debug
rem --specpath=newspec ^
rem --noconsole ^
rem --exclude-module=lib2to3 ^
pyi-makespec.exe ^
    --log-level=INFO ^
    --name=ccwin ^
    --runtime-hook=pyi-rthook_pyqt4.py ^
    --additional-hooks-dir=pyi-hooks ^
    --onedir ^
    --noupx ^
    ConsumerCheck\cc_start.py
