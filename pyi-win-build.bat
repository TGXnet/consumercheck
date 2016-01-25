@echo on
pyinstaller.exe ^
    --log-level=INFO ^
    --clean ^
    --noconfirm ^
    --distpath=pyi-build-cc-1.3.3 ^
    pyi-cc.win.spec
