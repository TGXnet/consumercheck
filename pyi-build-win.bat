@echo on
pyinstaller.exe ^
    --log-level=WARN ^
    --clean ^
    --noconfirm ^
    --icon win-cc.ico ^
    --workpath=pyi-workdir ^
    --distpath=pyi-dist-1.5.1 ^
    pyi-cc-win.spec
