@echo on
pyinstaller.exe ^
    --log-level=INFO ^
    --clean ^
    --noconfirm ^
    --icon win-cc.ico ^
    --workpath=pyi-workdir ^
    --distpath=pyi-dist-1.4.0 ^
    pyi-cc-win.spec
